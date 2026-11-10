// Copyright 2026 Rabimba Karanjai & Contributors.
// Licensed under the Apache License, Version 2.0.

package scorer

import (
	"fmt"
	"math"
	"math/rand/v2"
	"strings"
	"sync"
	"time"

	"github.com/rkaranjai/kubecon26-fleetkv-gke/router/pkg/hash"
	"github.com/rkaranjai/kubecon26-fleetkv-gke/router/pkg/metrics"
	"github.com/rkaranjai/kubecon26-fleetkv-gke/router/pkg/radix"
)

const (
	PolicyRoundRobin  = "round_robin"
	PolicyNaiveSticky = "naive_sticky"
	PolicyFleetKVFit  = "fleetkv_fit"

	PoolAuto   = "auto"
	PoolAgg    = "agg"
	PoolDisagg = "disagg"
)

// Config controls FleetKV scoring physics and HBM admission thresholds.
type Config struct {
	Policy                     string  `json:"policy"`
	Pool                       string  `json:"pool"`
	BlockSizeTokens            int     `json:"block_size_tokens"`
	SafetyReserveBlocks        int     `json:"safety_reserve_blocks"`
	PeakPrefillThresholdTokens int     `json:"peak_prefill_threshold_tokens"`
	BlockPrefillCostMs         float64 `json:"block_prefill_cost_ms"`
	HBMHitCostMs               float64 `json:"hbm_hit_cost_ms"`
	DRAMHitCostMs              float64 `json:"dram_hit_cost_ms"`
	PodThroughputTokPerMs      float64 `json:"pod_throughput_tok_per_ms"`
	ActiveDecodeWeightMs       float64 `json:"active_decode_weight_ms"`
}

// DefaultConfig returns production-calibrated TPU v6e defaults.
func DefaultConfig() Config {
	return Config{
		Policy:                     PolicyFleetKVFit,
		Pool:                       PoolAuto,
		BlockSizeTokens:            hash.DefaultBlockSize,
		SafetyReserveBlocks:        24,
		PeakPrefillThresholdTokens: 12288,
		BlockPrefillCostMs:         12.5,
		HBMHitCostMs:               0.25,
		DRAMHitCostMs:              0.90,
		PodThroughputTokPerMs:      20.48, // 256 tokens / 12.5 ms = 20.48 tok/ms
		ActiveDecodeWeightMs:       25.0,
	}
}

// RouteInput encapsulates a hashed incoming inference request.
type RouteInput struct {
	RequestID               string
	BlockHashes             []string
	TotalTokens             int
	MaxTokens               int
	BranchHorizonHintTokens int
	StageOverride           string
}

// RouteDecision describes the selected endpoint(s), metadata headers, and lease cleanup.
type RouteDecision struct {
	Timestamp             time.Time `json:"ts"`
	RequestID             string    `json:"request_id"`
	Policy                string    `json:"policy"`
	Pool                  string    `json:"pool"`
	Passthrough           bool      `json:"passthrough"`
	SelectedPodID         string    `json:"selected_pod_id"`
	TargetEndpoint        string    `json:"target_endpoint"`
	PrefillPodID          string    `json:"prefill_pod_id,omitempty"`
	PrefillEndpoint       string    `json:"prefill_endpoint,omitempty"`
	DecodePodID           string    `json:"decode_pod_id,omitempty"`
	DecodeEndpoint        string    `json:"decode_endpoint,omitempty"`
	MatchedHBMBlocks      int       `json:"matched_hbm_blocks"`
	MatchedDRAMBlocks     int       `json:"matched_dram_blocks"`
	TotalPromptBlocks     int       `json:"total_prompt_blocks"`
	EstimatedBranchBlocks int       `json:"estimated_branch_blocks"`
	Score                 float64   `json:"score"`
	Reason                string    `json:"reason"`
	Spillover             bool      `json:"spillover"`

	releasePrefillFn func()
	releaseFn        func()
}

// ReleasePrefill frees the in-flight prefill token queue reservation once TTFT (ResponseHeaders) completes.
func (d *RouteDecision) ReleasePrefill() {
	if d != nil && d.releasePrefillFn != nil {
		d.releasePrefillFn()
	}
}

// Release frees any in-flight HBM block and prefill token reservations associated with this route.
func (d *RouteDecision) Release() {
	if d != nil {
		if d.releasePrefillFn != nil {
			d.releasePrefillFn()
		}
		if d.releaseFn != nil {
			d.releaseFn()
		}
	}
}

// Engine executes thread-safe, hot-reloadable routing policies over a ClusterIndex.
type Engine struct {
	mu              sync.RWMutex
	cfg             Config
	index           *radix.ClusterIndex
	telemetry       *metrics.Telemetry
	recentMu        sync.Mutex
	recentDecisions []RouteDecision
	maxRecent       int
}

// NewEngine creates a policy scoring engine bound to index and telemetry.
func NewEngine(cfg Config, index *radix.ClusterIndex, telemetry *metrics.Telemetry) *Engine {
	if cfg.BlockSizeTokens <= 0 {
		cfg.BlockSizeTokens = hash.DefaultBlockSize
	}
	if cfg.BlockPrefillCostMs <= 0 {
		cfg.BlockPrefillCostMs = 12.5
	}
	if cfg.PodThroughputTokPerMs <= 0 {
		cfg.PodThroughputTokPerMs = 20.48
	}
	if cfg.ActiveDecodeWeightMs <= 0 {
		cfg.ActiveDecodeWeightMs = 25.0
	}
	if telemetry == nil {
		telemetry = metrics.NewTelemetry()
	}
	return &Engine{
		cfg:             cfg,
		index:           index,
		telemetry:       telemetry,
		recentDecisions: make([]RouteDecision, 0, 128),
		maxRecent:       128,
	}
}

// GetConfig returns the active scoring configuration.
func (e *Engine) GetConfig() Config {
	e.mu.RLock()
	defer e.mu.RUnlock()
	return e.cfg
}

// UpdatePolicy hot-reloads the active routing policy and optional pool mode ("agg"|"disagg"|"auto").
func (e *Engine) UpdatePolicy(policy, pool string) error {
	normPolicy := strings.ToLower(strings.TrimSpace(policy))
	switch normPolicy {
	case PolicyRoundRobin, PolicyNaiveSticky, PolicyFleetKVFit:
	default:
		return fmt.Errorf("unsupported policy %q (valid: round_robin, naive_sticky, fleetkv_fit)", policy)
	}

	normPool := strings.ToLower(strings.TrimSpace(pool))
	if normPool != "" {
		switch normPool {
		case PoolAuto, PoolAgg, PoolDisagg:
		default:
			return fmt.Errorf("unsupported pool %q (valid: auto, agg, disagg)", pool)
		}
	}

	e.mu.Lock()
	e.cfg.Policy = normPolicy
	if normPool != "" {
		e.cfg.Pool = normPool
	}
	e.mu.Unlock()
	return nil
}

// RecentDecisions returns up to limit recent routing decisions (newest last).
func (e *Engine) RecentDecisions(limit int) []RouteDecision {
	e.recentMu.Lock()
	defer e.recentMu.Unlock()
	n := len(e.recentDecisions)
	if limit <= 0 || limit > n {
		limit = n
	}
	out := make([]RouteDecision, limit)
	copy(out, e.recentDecisions[n-limit:])
	return out
}

func (e *Engine) recordDecision(dec RouteDecision) {
	targetLabel := dec.SelectedPodID
	if targetLabel == "" {
		targetLabel = "envoy_rr"
	}
	e.telemetry.RouteDecisionsTotal.WithLabelValues(dec.Policy, targetLabel, dec.Reason).Inc()
	if dec.Spillover {
		e.telemetry.HerdSpilloversTotal.Inc()
	}

	snapshot := dec
	snapshot.releasePrefillFn = nil
	snapshot.releaseFn = nil
	e.recentMu.Lock()
	if len(e.recentDecisions) >= e.maxRecent {
		copy(e.recentDecisions[0:], e.recentDecisions[1:])
		e.recentDecisions[len(e.recentDecisions)-1] = snapshot
	} else {
		e.recentDecisions = append(e.recentDecisions, snapshot)
	}
	e.recentMu.Unlock()
}

// Route selects an endpoint according to the active policy.
func (e *Engine) Route(in RouteInput) RouteDecision {
	cfg := e.GetConfig()
	policy := cfg.Policy
	pool := cfg.Pool

	switch strings.ToLower(strings.TrimSpace(in.StageOverride)) {
	case "stage1", PolicyRoundRobin:
		policy = PolicyRoundRobin
		pool = PoolAgg
	case "stage2", PolicyNaiveSticky:
		policy = PolicyNaiveSticky
		pool = PoolAgg
	case "stage3", PolicyFleetKVFit:
		policy = PolicyFleetKVFit
	}

	var dec RouteDecision
	switch policy {
	case PolicyRoundRobin:
		dec = RouteDecision{
			Timestamp:         time.Now(),
			RequestID:         in.RequestID,
			Policy:            PolicyRoundRobin,
			Pool:              PoolAgg,
			Passthrough:       true,
			TotalPromptBlocks: len(in.BlockHashes),
			Reason:            "stage1_round_robin",
		}
	case PolicyNaiveSticky:
		dec = e.routeNaiveSticky(cfg, pool, in)
	default:
		dec = e.routeFleetKVFit(cfg, pool, in)
	}

	e.recordDecision(dec)
	return dec
}

// routeNaiveSticky implements Stage 2: argmax_pod(MatchedHBMBlocks) with random tie-breaking.
func (e *Engine) routeNaiveSticky(cfg Config, pool string, in RouteInput) RouteDecision {
	roleFilter := radix.RoleAgg
	if pool == PoolDisagg {
		roleFilter = radix.RolePrefill
	}
	matches := e.index.MatchPods(in.BlockHashes, roleFilter)
	if len(matches) == 0 {
		matches = e.index.MatchPods(in.BlockHashes, "")
	}
	if len(matches) == 0 {
		return RouteDecision{
			Timestamp:         time.Now(),
			RequestID:         in.RequestID,
			Policy:            PolicyNaiveSticky,
			Pool:              pool,
			Passthrough:       true,
			TotalPromptBlocks: len(in.BlockHashes),
			Reason:            "no_pods_registered",
		}
	}

	bestBlocks := -1
	var tied []radix.PodPrefixMatch
	for _, m := range matches {
		if m.MatchedHBMBlocks > bestBlocks {
			bestBlocks = m.MatchedHBMBlocks
			tied = []radix.PodPrefixMatch{m}
		} else if m.MatchedHBMBlocks == bestBlocks {
			tied = append(tied, m)
		}
	}

	chosen := tied[0]
	if len(tied) > 1 {
		chosen = tied[rand.IntN(len(tied))]
	}

	unmatchedTokens := in.TotalTokens - chosen.MatchedHBMBlocks*cfg.BlockSizeTokens
	if unmatchedTokens < 0 {
		unmatchedTokens = 0
	}
	estBlocks := estimateBranchBlocks(unmatchedTokens, in.MaxTokens, in.BranchHorizonHintTokens, cfg.BlockSizeTokens)
	releasePrefill, release := e.index.AcquireStagedLease(chosen.Pod.PodID, estBlocks, unmatchedTokens)

	reason := "naive_longest_prefix"
	if chosen.MatchedHBMBlocks == 0 {
		reason = "naive_cold_random"
	}

	return RouteDecision{
		Timestamp:             time.Now(),
		RequestID:             in.RequestID,
		Policy:                PolicyNaiveSticky,
		Pool:                  radix.RoleAgg,
		SelectedPodID:         chosen.Pod.PodID,
		TargetEndpoint:        chosen.Pod.IPPort,
		MatchedHBMBlocks:      chosen.MatchedHBMBlocks,
		MatchedDRAMBlocks:     chosen.MatchedDRAMBlocks,
		TotalPromptBlocks:     len(in.BlockHashes),
		EstimatedBranchBlocks: estBlocks,
		Score:                 float64(chosen.MatchedHBMBlocks),
		Reason:                reason,
		releasePrefillFn:      releasePrefill,
		releaseFn:             release,
	}
}

// routeFleetKVFit implements Stage 3: HBM Fit Admission Gate + Disaggregated P/D Coordinator.
func (e *Engine) routeFleetKVFit(cfg Config, pool string, in RouteInput) RouteDecision {
	prefillMatches := e.index.MatchPods(in.BlockHashes, radix.RolePrefill)
	decodeMatches := e.index.MatchPods(in.BlockHashes, radix.RoleDecode)

	useDisagg := false
	if pool == PoolDisagg && len(prefillMatches) > 0 && len(decodeMatches) > 0 {
		useDisagg = true
	} else if pool == PoolAuto && len(prefillMatches) > 0 && len(decodeMatches) > 0 {
		useDisagg = true
	}

	if useDisagg {
		return e.routeDisaggFit(cfg, in, prefillMatches, decodeMatches)
	}

	aggMatches := e.index.MatchPods(in.BlockHashes, radix.RoleAgg)
	if len(aggMatches) == 0 {
		aggMatches = e.index.MatchPods(in.BlockHashes, "")
	}
	if len(aggMatches) == 0 {
		return RouteDecision{
			Timestamp:         time.Now(),
			RequestID:         in.RequestID,
			Policy:            PolicyFleetKVFit,
			Pool:              PoolAgg,
			Passthrough:       true,
			TotalPromptBlocks: len(in.BlockHashes),
			Reason:            "no_pods_registered",
		}
	}

	return e.routeAggFit(cfg, in, aggMatches)
}

func (e *Engine) routeAggFit(cfg Config, in RouteInput, matches []radix.PodPrefixMatch) RouteDecision {
	// Identify which pod naive longest-prefix would have picked to detect herd spillover.
	naiveTopPodID := ""
	naiveTopBlocks := 0
	for _, m := range matches {
		if m.TotalMatchedBlocks() > naiveTopBlocks {
			naiveTopBlocks = m.TotalMatchedBlocks()
			naiveTopPodID = m.Pod.PodID
		}
	}

	hbmSavedPerBlock := cfg.BlockPrefillCostMs - cfg.HBMHitCostMs
	dramSavedPerBlock := cfg.BlockPrefillCostMs - cfg.DRAMHitCostMs

	bestScore := -math.MaxFloat64
	var bestMatch *radix.PodPrefixMatch
	bestEstBlocks := 1
	bestUnmatched := 0

	for i := range matches {
		m := &matches[i]
		unmatchedToks := in.TotalTokens - m.TotalMatchedBlocks()*cfg.BlockSizeTokens
		if unmatchedToks < 0 {
			unmatchedToks = 0
		}
		estBlocks := estimateBranchBlocks(unmatchedToks, in.MaxTokens, in.BranchHorizonHintTokens, cfg.BlockSizeTokens)

		// 1. Hard HBM Fit Admission Gate + Peak Prefill Queue Gate
		if m.Pod.EffectiveFreeHBMBlocks() < estBlocks+cfg.SafetyReserveBlocks {
			continue
		}
		if cfg.PeakPrefillThresholdTokens > 0 && m.Pod.InFlightPrefillTokens > cfg.PeakPrefillThresholdTokens {
			continue
		}

		// 2. Marginal saved prefill ms minus live queue wait ms
		marginalSavedMs := float64(m.MatchedHBMBlocks)*hbmSavedPerBlock + float64(m.MatchedDRAMBlocks)*dramSavedPerBlock
		queueWaitMs := float64(m.Pod.InFlightPrefillTokens)/cfg.PodThroughputTokPerMs +
			float64(m.Pod.ActiveRequests)*cfg.ActiveDecodeWeightMs +
			float64(m.Pod.ReservedBlocks)*0.05
		score := marginalSavedMs - queueWaitMs

		if score > bestScore {
			bestScore = score
			bestMatch = m
			bestEstBlocks = estBlocks
			bestUnmatched = unmatchedToks
		}
	}

	spillover := false
	reason := "fleetkv_fit_optimal"

	if bestMatch == nil {
		// All pods under saturation: fall back to pod with highest remaining HBM & lowest queue.
		fallbackIdx := 0
		bestFallback := -math.MaxFloat64
		for i, m := range matches {
			fbScore := float64(m.Pod.EffectiveFreeHBMBlocks())*2.0 - float64(m.Pod.InFlightPrefillTokens)*0.05 - float64(m.Pod.ActiveRequests)*20.0
			if fbScore > bestFallback {
				bestFallback = fbScore
				fallbackIdx = i
			}
		}
		bestMatch = &matches[fallbackIdx]
		bestUnmatched = in.TotalTokens - bestMatch.TotalMatchedBlocks()*cfg.BlockSizeTokens
		if bestUnmatched < 0 {
			bestUnmatched = 0
		}
		bestEstBlocks = estimateBranchBlocks(bestUnmatched, in.MaxTokens, in.BranchHorizonHintTokens, cfg.BlockSizeTokens)
		bestScore = bestFallback
		reason = "cluster_pressure_least_loaded"
		if naiveTopBlocks > 0 && bestMatch.Pod.PodID != naiveTopPodID {
			spillover = true
		}
	} else if naiveTopBlocks > 0 && bestMatch.Pod.PodID != naiveTopPodID {
		spillover = true
		reason = "herd_spillover"
	} else if bestMatch.TotalMatchedBlocks() == 0 {
		reason = "cold_fit_balanced"
	}

	releasePrefill, release := e.index.AcquireStagedLease(bestMatch.Pod.PodID, bestEstBlocks, bestUnmatched)

	return RouteDecision{
		Timestamp:             time.Now(),
		RequestID:             in.RequestID,
		Policy:                PolicyFleetKVFit,
		Pool:                  PoolAgg,
		SelectedPodID:         bestMatch.Pod.PodID,
		TargetEndpoint:        bestMatch.Pod.IPPort,
		MatchedHBMBlocks:      bestMatch.MatchedHBMBlocks,
		MatchedDRAMBlocks:     bestMatch.MatchedDRAMBlocks,
		TotalPromptBlocks:     len(in.BlockHashes),
		EstimatedBranchBlocks: bestEstBlocks,
		Score:                 bestScore,
		Reason:                reason,
		Spillover:             spillover,
		releasePrefillFn:      releasePrefill,
		releaseFn:             release,
	}
}

func (e *Engine) routeDisaggFit(
	cfg Config,
	in RouteInput,
	prefillMatches []radix.PodPrefixMatch,
	decodeMatches []radix.PodPrefixMatch,
) RouteDecision {
	hbmSavedPerBlock := cfg.BlockPrefillCostMs - cfg.HBMHitCostMs
	dramSavedPerBlock := cfg.BlockPrefillCostMs - cfg.DRAMHitCostMs

	// Step 1: Select optimal Prefill pod via marginal_saved_prefill_ms - queue_wait_ms
	// counting both HBM and Tier-2 Host DRAM blocks (TPUConnectorHMA).
	bestPrefillScore := -math.MaxFloat64
	bestPrefillIdx := 0
	prefillTopID := ""
	prefillTopBlocks := 0
	for _, pm := range prefillMatches {
		if pm.TotalMatchedBlocks() > prefillTopBlocks {
			prefillTopBlocks = pm.TotalMatchedBlocks()
			prefillTopID = pm.Pod.PodID
		}
	}

	prefillThroughput := cfg.PodThroughputTokPerMs * 8.0
	for i, pm := range prefillMatches {
		savedMs := float64(pm.MatchedHBMBlocks)*hbmSavedPerBlock + float64(pm.MatchedDRAMBlocks)*dramSavedPerBlock
		if prefillTopBlocks >= 16 && pm.TotalMatchedBlocks() < prefillTopBlocks/2 {
			savedMs -= float64(prefillTopBlocks-pm.TotalMatchedBlocks()) * cfg.BlockPrefillCostMs
		}
		queueWaitMs := float64(pm.Pod.InFlightPrefillTokens)/prefillThroughput +
			float64(pm.Pod.ActiveRequests)*20.0 -
			float64(pm.Pod.EffectiveFreeHBMBlocks())*0.15
		score := savedMs - queueWaitMs
		if i == 0 || score > bestPrefillScore {
			bestPrefillScore = score
			bestPrefillIdx = i
		}
	}
	chosenPrefill := prefillMatches[bestPrefillIdx]
	prefillUnmatchedToks := in.TotalTokens - chosenPrefill.TotalMatchedBlocks()*cfg.BlockSizeTokens
	if prefillUnmatchedToks < 0 {
		prefillUnmatchedToks = 0
	}

	// Step 2: Select least-loaded Decode pod satisfying the HBM Fit Gate.
	estDecodeDeltaBlocks := estimateBranchBlocks(prefillUnmatchedToks, in.MaxTokens, in.BranchHorizonHintTokens, cfg.BlockSizeTokens)

	decodeTopID := ""
	decodeTopBlocks := 0
	for _, dm := range decodeMatches {
		if dm.MatchedHBMBlocks > decodeTopBlocks {
			decodeTopBlocks = dm.MatchedHBMBlocks
			decodeTopID = dm.Pod.PodID
		}
	}

	bestDecodeScore := -math.MaxFloat64
	bestDecodeIdx := -1
	for i, dm := range decodeMatches {
		if dm.Pod.EffectiveFreeHBMBlocks() < estDecodeDeltaBlocks+cfg.SafetyReserveBlocks {
			continue
		}
		// Spread concurrent active decode branches evenly while rewarding warm decode HBM blocks.
		score := float64(dm.MatchedHBMBlocks)*1.5 -
			float64(dm.Pod.ActiveRequests)*cfg.ActiveDecodeWeightMs +
			float64(dm.Pod.EffectiveFreeHBMBlocks())*0.20
		if bestDecodeIdx == -1 || score > bestDecodeScore {
			bestDecodeScore = score
			bestDecodeIdx = i
		}
	}

	spillover := false
	reason := "disagg_pd_fit"
	if bestDecodeIdx == -1 {
		// Fallback to decode pod with maximum free HBM headroom.
		bestDecodeIdx = 0
		for i, dm := range decodeMatches {
			if dm.Pod.EffectiveFreeHBMBlocks()-dm.Pod.ActiveRequests*4 >
				decodeMatches[bestDecodeIdx].Pod.EffectiveFreeHBMBlocks()-decodeMatches[bestDecodeIdx].Pod.ActiveRequests*4 {
				bestDecodeIdx = i
			}
		}
		reason = "disagg_pressure_least_loaded"
		spillover = true
	} else {
		chosenDecode := decodeMatches[bestDecodeIdx]
		if (prefillTopBlocks > 0 && chosenPrefill.Pod.PodID != prefillTopID) ||
			(decodeTopBlocks > 0 && chosenDecode.Pod.PodID != decodeTopID) {
			spillover = true
			reason = "herd_spillover"
		}
	}

	chosenDecode := decodeMatches[bestDecodeIdx]

	releasePrefillQ, releasePrefill := e.index.AcquireStagedLease(chosenPrefill.Pod.PodID, 1, prefillUnmatchedToks)
	_, releaseDecode := e.index.AcquireStagedLease(chosenDecode.Pod.PodID, estDecodeDeltaBlocks, 0)

	return RouteDecision{
		Timestamp:             time.Now(),
		RequestID:             in.RequestID,
		Policy:                PolicyFleetKVFit,
		Pool:                  PoolDisagg,
		SelectedPodID:         chosenDecode.Pod.PodID,
		TargetEndpoint:        chosenDecode.Pod.IPPort,
		PrefillPodID:          chosenPrefill.Pod.PodID,
		PrefillEndpoint:       chosenPrefill.Pod.IPPort,
		DecodePodID:           chosenDecode.Pod.PodID,
		DecodeEndpoint:        chosenDecode.Pod.IPPort,
		MatchedHBMBlocks:      chosenPrefill.MatchedHBMBlocks,
		MatchedDRAMBlocks:     chosenPrefill.MatchedDRAMBlocks,
		TotalPromptBlocks:     len(in.BlockHashes),
		EstimatedBranchBlocks: estDecodeDeltaBlocks,
		Score:                 bestPrefillScore + bestDecodeScore,
		Reason:                reason,
		Spillover:             spillover,
		releasePrefillFn:      releasePrefillQ,
		releaseFn: func() {
			releasePrefill()
			releaseDecode()
		},
	}
}

func estimateBranchBlocks(unmatchedPromptTokens, maxTokens, horizonHintTokens, blockSize int) int {
	if blockSize <= 0 {
		blockSize = hash.DefaultBlockSize
	}
	if maxTokens <= 0 {
		maxTokens = 64
	}
	totalDelta := unmatchedPromptTokens + maxTokens + horizonHintTokens
	if totalDelta <= 0 {
		return 1
	}
	blocks := (totalDelta + blockSize - 1) / blockSize
	if blocks < 1 {
		return 1
	}
	return blocks
}
