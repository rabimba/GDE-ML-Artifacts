// Copyright 2026 Rabimba Karanjai & Contributors.
// Licensed under the Apache License, Version 2.0.

package radix

import (
	"fmt"
	"net"
	"sort"
	"strings"
	"sync"
	"time"

	"github.com/rkaranjai/kubecon26-fleetkv-gke/router/pkg/metrics"
)

const (
	TierHBM  = "hbm"
	TierDRAM = "dram"

	RoleAgg     = "agg"
	RolePrefill = "prefill"
	RoleDecode  = "decode"
)

// KVEvent matches the ZeroMQ PUB payload emitted by vLLM --kv-events-config and twin workers.
type KVEvent struct {
	EventType         string   `json:"event_type" msgpack:"event_type"`
	PodID             string   `json:"pod_id" msgpack:"pod_id"`
	IPPort            string   `json:"ip_port" msgpack:"ip_port"`
	Role              string   `json:"role" msgpack:"role"`
	ParentBlockHash   string   `json:"parent_block_hash,omitempty" msgpack:"parent_block_hash,omitempty"`
	BlockHashes       []string `json:"block_hashes" msgpack:"block_hashes"`
	FreeHBMBlocks     int      `json:"free_hbm_blocks" msgpack:"free_hbm_blocks"`
	HBMCapacityBlocks int      `json:"hbm_capacity_blocks,omitempty" msgpack:"hbm_capacity_blocks,omitempty"`
	FreeDRAMBlocks    int      `json:"free_dram_blocks,omitempty" msgpack:"free_dram_blocks,omitempty"`
	Tier              string   `json:"tier" msgpack:"tier"`
	TimestampUnixMs   int64    `json:"ts_ms,omitempty" msgpack:"ts_ms,omitempty"`
}

// PodState snapshots both ZMQ-reported block capacity and live router-side in-flight load.
type PodState struct {
	PodID                 string    `json:"pod_id"`
	IPPort                string    `json:"ip_port"`
	RawAddress            string    `json:"raw_address"`
	Role                  string    `json:"role"`
	FreeHBMBlocks         int       `json:"free_hbm_blocks"`
	HBMCapacityBlocks     int       `json:"hbm_capacity_blocks"`
	FreeDRAMBlocks        int       `json:"free_dram_blocks"`
	IndexedHBMBlocks      int       `json:"indexed_hbm_blocks"`
	IndexedDRAMBlocks     int       `json:"indexed_dram_blocks"`
	ReservedBlocks        int       `json:"reserved_blocks"`
	InFlightPrefillTokens int       `json:"inflight_prefill_tokens"`
	ActiveRequests        int       `json:"active_requests"`
	EvictionsTotal        uint64    `json:"evictions_total"`
	LastUpdated           time.Time `json:"last_updated"`
}

// EffectiveFreeHBMBlocks returns remaining unreserved HBM blocks available for new admissions.
func (p PodState) EffectiveFreeHBMBlocks() int {
	free := p.FreeHBMBlocks - p.ReservedBlocks
	if free < 0 {
		return 0
	}
	return free
}

// PodPrefixMatch captures contiguous prefix blocks matched on a specific pod across tiers.
type PodPrefixMatch struct {
	Pod               PodState
	MatchedHBMBlocks  int
	MatchedDRAMBlocks int
}

// TotalMatchedBlocks returns combined HBM + Tier-2 Host DRAM contiguous prefix blocks.
func (m PodPrefixMatch) TotalMatchedBlocks() int {
	return m.MatchedHBMBlocks + m.MatchedDRAMBlocks
}

type radixNode struct {
	hash     string
	parent   *radixNode
	children map[string]*radixNode
	hbmPods  map[string]struct{}
	dramPods map[string]struct{}
}

func newRadixNode(hash string, parent *radixNode) *radixNode {
	return &radixNode{
		hash:     hash,
		parent:   parent,
		children: make(map[string]*radixNode),
		hbmPods:  make(map[string]struct{}),
		dramPods: make(map[string]struct{}),
	}
}

// ClusterIndex maintains a thread-safe Radix Tree of 256-token KV blocks and per-pod HBM accounting.
type ClusterIndex struct {
	mu          sync.RWMutex
	root        *radixNode
	nodesByHash map[string]*radixNode
	pods        map[string]*PodState
	podHBMSet   map[string]map[string]struct{}
	podDRAMSet  map[string]map[string]struct{}
	telemetry   *metrics.Telemetry
}

// NewClusterIndex creates an empty concurrency-safe Radix KV index.
func NewClusterIndex(telemetry *metrics.Telemetry) *ClusterIndex {
	if telemetry == nil {
		telemetry = metrics.NewTelemetry()
	}
	return &ClusterIndex{
		root:        newRadixNode("", nil),
		nodesByHash: make(map[string]*radixNode),
		pods:        make(map[string]*PodState),
		podHBMSet:   make(map[string]map[string]struct{}),
		podDRAMSet:  make(map[string]map[string]struct{}),
		telemetry:   telemetry,
	}
}

// ResolveNumericIPPort resolves host:port into numeric IPv4:port required by Envoy ORIGINAL_DST.
func ResolveNumericIPPort(addr string) string {
	addr = strings.TrimSpace(addr)
	if addr == "" {
		return ""
	}
	host, port, err := net.SplitHostPort(addr)
	if err != nil {
		return addr
	}
	if ip := net.ParseIP(host); ip != nil {
		return net.JoinHostPort(ip.String(), port)
	}
	ips, err := net.LookupIP(host)
	if err != nil || len(ips) == 0 {
		return addr
	}
	for _, ip := range ips {
		if v4 := ip.To4(); v4 != nil {
			return net.JoinHostPort(v4.String(), port)
		}
	}
	return net.JoinHostPort(ips[0].String(), port)
}

// UpsertStaticPod pre-registers a serving endpoint before its first ZMQ event arrives.
func (idx *ClusterIndex) UpsertStaticPod(podID, ipPort, role string, hbmCapacityBlocks int) {
	idx.mu.Lock()
	defer idx.mu.Unlock()

	if hbmCapacityBlocks <= 0 {
		hbmCapacityBlocks = 360
	}
	resolved := ResolveNumericIPPort(ipPort)
	p, exists := idx.pods[podID]
	if !exists {
		p = &PodState{
			PodID:             podID,
			IPPort:            resolved,
			RawAddress:        ipPort,
			Role:              normalizeRole(role),
			FreeHBMBlocks:     hbmCapacityBlocks,
			HBMCapacityBlocks: hbmCapacityBlocks,
			LastUpdated:       time.Now(),
		}
		idx.pods[podID] = p
		idx.podHBMSet[podID] = make(map[string]struct{})
		idx.podDRAMSet[podID] = make(map[string]struct{})
	} else {
		if resolved != "" {
			p.IPPort = resolved
			p.RawAddress = ipPort
		}
		if role != "" {
			p.Role = normalizeRole(role)
		}
		if p.HBMCapacityBlocks == 0 {
			p.HBMCapacityBlocks = hbmCapacityBlocks
			p.FreeHBMBlocks = hbmCapacityBlocks
		}
		p.LastUpdated = time.Now()
	}
	idx.telemetry.PodFreeHBMBlocks.WithLabelValues(p.PodID, p.Role).Set(float64(p.FreeHBMBlocks))
}

func normalizeRole(role string) string {
	switch strings.ToLower(strings.TrimSpace(role)) {
	case RolePrefill:
		return RolePrefill
	case RoleDecode:
		return RoleDecode
	default:
		return RoleAgg
	}
}

func normalizeTier(tier string) string {
	if strings.EqualFold(strings.TrimSpace(tier), TierDRAM) {
		return TierDRAM
	}
	return TierHBM
}

// ApplyEvent ingests a BlockStored, BlockRemoved, or Heartbeat ZMQ event in sub-millisecond time.
func (idx *ClusterIndex) ApplyEvent(ev KVEvent) error {
	if ev.PodID == "" {
		return fmt.Errorf("kv event missing pod_id")
	}

	tier := normalizeTier(ev.Tier)

	idx.mu.Lock()
	defer idx.mu.Unlock()

	p, exists := idx.pods[ev.PodID]
	if !exists {
		capBlocks := ev.HBMCapacityBlocks
		if capBlocks <= 0 {
			capBlocks = 360
		}
		freeBlocks := ev.FreeHBMBlocks
		if freeBlocks <= 0 && ev.EventType != "BlockStored" {
			freeBlocks = capBlocks
		}
		p = &PodState{
			PodID:             ev.PodID,
			IPPort:            ResolveNumericIPPort(ev.IPPort),
			RawAddress:        ev.IPPort,
			Role:              normalizeRole(ev.Role),
			FreeHBMBlocks:     freeBlocks,
			HBMCapacityBlocks: capBlocks,
			FreeDRAMBlocks:    ev.FreeDRAMBlocks,
			LastUpdated:       time.Now(),
		}
		idx.pods[ev.PodID] = p
		idx.podHBMSet[ev.PodID] = make(map[string]struct{})
		idx.podDRAMSet[ev.PodID] = make(map[string]struct{})
	} else {
		if ev.IPPort != "" && ev.IPPort != p.RawAddress {
			p.RawAddress = ev.IPPort
			p.IPPort = ResolveNumericIPPort(ev.IPPort)
		}
		if ev.Role != "" {
			p.Role = normalizeRole(ev.Role)
		}
		if ev.HBMCapacityBlocks > 0 {
			p.HBMCapacityBlocks = ev.HBMCapacityBlocks
		}
		if ev.FreeHBMBlocks >= 0 {
			p.FreeHBMBlocks = ev.FreeHBMBlocks
		}
		if ev.FreeDRAMBlocks >= 0 {
			p.FreeDRAMBlocks = ev.FreeDRAMBlocks
		}
		p.LastUpdated = time.Now()
	}

	switch ev.EventType {
	case "BlockStored":
		parentNode := idx.root
		if ev.ParentBlockHash != "" {
			if existingParent, ok := idx.nodesByHash[ev.ParentBlockHash]; ok {
				parentNode = existingParent
			}
		}
		for _, bh := range ev.BlockHashes {
			if bh == "" {
				continue
			}
			node, ok := idx.nodesByHash[bh]
			if !ok {
				node = newRadixNode(bh, parentNode)
				parentNode.children[bh] = node
				idx.nodesByHash[bh] = node
			} else if parentNode != idx.root && node.parent == idx.root {
				// Re-parent root-attached node if its true prefix parent arrived later.
				delete(idx.root.children, bh)
				node.parent = parentNode
				parentNode.children[bh] = node
			}

			if tier == TierDRAM {
				node.dramPods[ev.PodID] = struct{}{}
				idx.podDRAMSet[ev.PodID][bh] = struct{}{}
			} else {
				node.hbmPods[ev.PodID] = struct{}{}
				idx.podHBMSet[ev.PodID][bh] = struct{}{}
			}
			parentNode = node
		}

	case "BlockRemoved":
		for _, bh := range ev.BlockHashes {
			node, ok := idx.nodesByHash[bh]
			if !ok {
				continue
			}
			if tier == TierDRAM {
				delete(node.dramPods, ev.PodID)
				delete(idx.podDRAMSet[ev.PodID], bh)
			} else {
				if _, wasPresent := node.hbmPods[ev.PodID]; wasPresent {
					delete(node.hbmPods, ev.PodID)
					delete(idx.podHBMSet[ev.PodID], bh)
					p.EvictionsTotal++
					idx.telemetry.PodEvictionsTotal.WithLabelValues(ev.PodID).Inc()
				}
			}
			idx.pruneIfEmptyLocked(node)
		}

	case "AllBlocksCleared":
		for bh := range idx.podHBMSet[ev.PodID] {
			if node, ok := idx.nodesByHash[bh]; ok {
				delete(node.hbmPods, ev.PodID)
				idx.pruneIfEmptyLocked(node)
			}
		}
		for bh := range idx.podDRAMSet[ev.PodID] {
			if node, ok := idx.nodesByHash[bh]; ok {
				delete(node.dramPods, ev.PodID)
				idx.pruneIfEmptyLocked(node)
			}
		}
		idx.podHBMSet[ev.PodID] = make(map[string]struct{})
		idx.podDRAMSet[ev.PodID] = make(map[string]struct{})
	}

	p.IndexedHBMBlocks = len(idx.podHBMSet[ev.PodID])
	p.IndexedDRAMBlocks = len(idx.podDRAMSet[ev.PodID])

	idx.telemetry.ZMQEventsTotal.WithLabelValues(ev.EventType, ev.PodID, tier).Inc()
	idx.telemetry.RadixBlocksTotal.Set(float64(len(idx.nodesByHash)))
	idx.telemetry.PodFreeHBMBlocks.WithLabelValues(p.PodID, p.Role).Set(float64(p.FreeHBMBlocks))
	return nil
}

func (idx *ClusterIndex) pruneIfEmptyLocked(node *radixNode) {
	curr := node
	for curr != nil && curr != idx.root {
		if len(curr.hbmPods) > 0 || len(curr.dramPods) > 0 || len(curr.children) > 0 {
			return
		}
		parent := curr.parent
		if parent != nil {
			delete(parent.children, curr.hash)
		}
		delete(idx.nodesByHash, curr.hash)
		curr = parent
	}
}

// MatchPods walks the contiguous blockHash sequence against the Radix Tree for all pods matching roleFilter.
// If roleFilter is empty, all registered pods are evaluated.
func (idx *ClusterIndex) MatchPods(blockHashes []string, roleFilter string) []PodPrefixMatch {
	idx.mu.RLock()
	defer idx.mu.RUnlock()

	results := make([]PodPrefixMatch, 0, len(idx.pods))
	podIDs := make([]string, 0, len(idx.pods))
	for id, p := range idx.pods {
		if roleFilter != "" && p.Role != roleFilter {
			continue
		}
		podIDs = append(podIDs, id)
	}
	sort.Strings(podIDs)

	for _, podID := range podIDs {
		p := *idx.pods[podID]
		matchedHBM := 0
		matchedDRAM := 0

		curr := idx.root
		for i, bh := range blockHashes {
			var next *radixNode
			if curr != nil {
				next = curr.children[bh]
			}
			if next == nil {
				// Fallback to hash-indexed node in case parent block arrived out-of-order.
				next = idx.nodesByHash[bh]
			}
			if next == nil {
				break
			}
			_, inHBM := next.hbmPods[podID]
			_, inDRAM := next.dramPods[podID]
			if !inHBM && !inDRAM {
				// Contiguous prefix broken at block index i.
				_ = i
				break
			}
			if inHBM {
				matchedHBM++
			} else if inDRAM {
				matchedDRAM++
			}
			curr = next
		}

		results = append(results, PodPrefixMatch{
			Pod:               p,
			MatchedHBMBlocks:  matchedHBM,
			MatchedDRAMBlocks: matchedDRAM,
		})
	}
	return results
}

// AcquireLease atomically reserves estimated HBM blocks and in-flight prefill tokens on a pod.
// Calling the returned release closure is idempotent and decrements the reservation.
func (idx *ClusterIndex) AcquireLease(podID string, reservedBlocks int, prefillTokens int) func() {
	_, releaseAll := idx.AcquireStagedLease(podID, reservedBlocks, prefillTokens)
	return releaseAll
}

// AcquireStagedLease reserves HBM blocks, in-flight prefill tokens, and active request count.
// releasePrefill releases only the prefill token queue reservation once TTFT (ResponseHeaders) completes;
// releaseAll is idempotent and releases prefill tokens (if not yet released), HBM blocks, and active request count.
func (idx *ClusterIndex) AcquireStagedLease(podID string, reservedBlocks int, prefillTokens int) (func(), func()) {
	if reservedBlocks < 0 {
		reservedBlocks = 0
	}
	if prefillTokens < 0 {
		prefillTokens = 0
	}

	idx.mu.Lock()
	if p, ok := idx.pods[podID]; ok {
		p.ReservedBlocks += reservedBlocks
		p.InFlightPrefillTokens += prefillTokens
		p.ActiveRequests++
	}
	idx.mu.Unlock()

	var prefillOnce sync.Once
	releasePrefill := func() {
		prefillOnce.Do(func() {
			if prefillTokens == 0 {
				return
			}
			idx.mu.Lock()
			defer idx.mu.Unlock()
			if p, ok := idx.pods[podID]; ok {
				p.InFlightPrefillTokens -= prefillTokens
				if p.InFlightPrefillTokens < 0 {
					p.InFlightPrefillTokens = 0
				}
			}
		})
	}

	var allOnce sync.Once
	releaseAll := func() {
		releasePrefill()
		allOnce.Do(func() {
			idx.mu.Lock()
			defer idx.mu.Unlock()
			if p, ok := idx.pods[podID]; ok {
				p.ReservedBlocks -= reservedBlocks
				if p.ReservedBlocks < 0 {
					p.ReservedBlocks = 0
				}
				p.ActiveRequests--
				if p.ActiveRequests < 0 {
					p.ActiveRequests = 0
				}
			}
		})
	}

	return releasePrefill, releaseAll
}

// SnapshotPods returns a deterministic sorted copy of all registered pod states.
func (idx *ClusterIndex) SnapshotPods() []PodState {
	idx.mu.RLock()
	defer idx.mu.RUnlock()

	out := make([]PodState, 0, len(idx.pods))
	for _, p := range idx.pods {
		out = append(out, *p)
	}
	sort.Slice(out, func(i, j int) bool {
		return out[i].PodID < out[j].PodID
	})
	return out
}

// TotalIndexedBlocks returns total unique block hashes currently stored across the cluster.
func (idx *ClusterIndex) TotalIndexedBlocks() int {
	idx.mu.RLock()
	defer idx.mu.RUnlock()
	return len(idx.nodesByHash)
}

// ClearBlocks clears all indexed blocks across pods while preserving registered pod endpoints.
func (idx *ClusterIndex) ClearBlocks() {
	idx.mu.Lock()
	defer idx.mu.Unlock()
	idx.root = newRadixNode("", nil)
	idx.nodesByHash = make(map[string]*radixNode)
	for podID, p := range idx.pods {
		idx.podHBMSet[podID] = make(map[string]struct{})
		idx.podDRAMSet[podID] = make(map[string]struct{})
		p.IndexedHBMBlocks = 0
		p.IndexedDRAMBlocks = 0
		p.FreeHBMBlocks = p.HBMCapacityBlocks
		p.EvictionsTotal = 0
		idx.telemetry.PodFreeHBMBlocks.WithLabelValues(p.PodID, p.Role).Set(float64(p.FreeHBMBlocks))
	}
	idx.telemetry.RadixBlocksTotal.Set(0)
}
