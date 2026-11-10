// Copyright 2026 Rabimba Karanjai & Contributors.
// Licensed under the Apache License, Version 2.0.

package scorer_test

import (
	"fmt"
	"testing"

	"github.com/rkaranjai/kubecon26-fleetkv-gke/router/pkg/metrics"
	"github.com/rkaranjai/kubecon26-fleetkv-gke/router/pkg/radix"
	"github.com/rkaranjai/kubecon26-fleetkv-gke/router/pkg/scorer"
)

func makeTrunk(numBlocks int) []string {
	out := make([]string, numBlocks)
	for i := range out {
		out[i] = fmt.Sprintf("trunk_%010d", i)
	}
	return out
}

func TestNaiveStickyHerdsEightWayForkOntoSinglePod(t *testing.T) {
	tel := metrics.NewTelemetry()
	idx := radix.NewClusterIndex(tel)
	idx.UpsertStaticPod("agg-0", "127.0.0.1:8001", "agg", 360)
	idx.UpsertStaticPod("agg-1", "127.0.0.1:8002", "agg", 360)
	idx.UpsertStaticPod("agg-2", "127.0.0.1:8003", "agg", 360)
	idx.UpsertStaticPod("agg-3", "127.0.0.1:8004", "agg", 360)

	trunk := makeTrunk(80) // 20,480-token shared trunk on agg-0
	_ = idx.ApplyEvent(radix.KVEvent{
		EventType:     "BlockStored",
		PodID:         "agg-0",
		Role:          "agg",
		BlockHashes:   trunk,
		FreeHBMBlocks: 160,
		Tier:          "hbm",
	})

	cfg := scorer.DefaultConfig()
	cfg.Policy = scorer.PolicyNaiveSticky
	cfg.Pool = scorer.PoolAgg
	eng := scorer.NewEngine(cfg, idx, tel)

	var leases []scorer.RouteDecision
	defer func() {
		for i := range leases {
			leases[i].Release()
		}
	}()

	for b := 0; b < 8; b++ {
		branchHashes := append([]string{}, trunk...)
		for d := 0; d < 16; d++ {
			branchHashes = append(branchHashes, fmt.Sprintf("b%d_d%d", b, d))
		}
		dec := eng.Route(scorer.RouteInput{
			RequestID:               fmt.Sprintf("fork-%d", b),
			BlockHashes:             branchHashes,
			TotalTokens:             len(branchHashes) * 256,
			MaxTokens:               512,
			BranchHorizonHintTokens: 8192,
		})
		leases = append(leases, dec)
		if dec.SelectedPodID != "agg-0" {
			t.Fatalf("expected naive_sticky to herd branch %d onto agg-0, got %s", b, dec.SelectedPodID)
		}
	}
}

func TestFleetKVFitHBMGateTriggersSpilloverAcrossPods(t *testing.T) {
	tel := metrics.NewTelemetry()
	idx := radix.NewClusterIndex(tel)
	idx.UpsertStaticPod("agg-0", "127.0.0.1:8001", "agg", 360)
	idx.UpsertStaticPod("agg-1", "127.0.0.1:8002", "agg", 360)

	trunk := makeTrunk(80)
	// agg-0 holds 80 trunk blocks and has 150 free HBM blocks remaining.
	_ = idx.ApplyEvent(radix.KVEvent{
		EventType:     "BlockStored",
		PodID:         "agg-0",
		Role:          "agg",
		BlockHashes:   trunk,
		FreeHBMBlocks: 150,
		Tier:          "hbm",
	})

	cfg := scorer.DefaultConfig()
	cfg.Policy = scorer.PolicyFleetKVFit
	cfg.Pool = scorer.PoolAgg
	cfg.SafetyReserveBlocks = 24
	eng := scorer.NewEngine(cfg, idx, tel)

	podCounts := map[string]int{}
	spillovers := 0
	var leases []scorer.RouteDecision
	defer func() {
		for i := range leases {
			leases[i].Release()
		}
	}()

	// Fire 8 concurrent forked branches, each with 8 blocks delta + 8192 horizon hint (~41 est blocks).
	// agg-0 has 150 free blocks (24 reserve -> 126 usable -> fits at most 3 branches before spilling!).
	for b := 0; b < 8; b++ {
		branchHashes := append([]string{}, trunk...)
		for d := 0; d < 8; d++ {
			branchHashes = append(branchHashes, fmt.Sprintf("fork_%d_blk_%d", b, d))
		}
		dec := eng.Route(scorer.RouteInput{
			RequestID:               fmt.Sprintf("fit-fork-%d", b),
			BlockHashes:             branchHashes,
			TotalTokens:             len(branchHashes) * 256,
			MaxTokens:               256,
			BranchHorizonHintTokens: 8192,
		})
		leases = append(leases, dec)
		podCounts[dec.SelectedPodID]++
		if dec.Spillover {
			spillovers++
		}
	}

	if podCounts["agg-0"] == 8 || podCounts["agg-1"] == 0 {
		t.Fatalf("expected FleetKV HBM Fit Gate to spread branches across agg-0 and agg-1; got %+v", podCounts)
	}
	if spillovers == 0 {
		t.Fatalf("expected herd_spillover events > 0, got 0")
	}
}

func TestFleetKVDisaggregatedPrefillDecodeCoordination(t *testing.T) {
	tel := metrics.NewTelemetry()
	idx := radix.NewClusterIndex(tel)
	idx.UpsertStaticPod("prefill-0", "127.0.0.1:8003", "prefill", 360)
	idx.UpsertStaticPod("decode-0", "127.0.0.1:8004", "decode", 360)
	idx.UpsertStaticPod("decode-1", "127.0.0.1:8005", "decode", 360)

	trunk := makeTrunk(80)
	// Store 50 blocks in HBM and 30 blocks in Tier-2 Host DRAM (TPUConnectorHMA) on prefill-0.
	_ = idx.ApplyEvent(radix.KVEvent{
		EventType:     "BlockStored",
		PodID:         "prefill-0",
		Role:          "prefill",
		BlockHashes:   trunk[:50],
		FreeHBMBlocks: 310,
		Tier:          "hbm",
	})
	_ = idx.ApplyEvent(radix.KVEvent{
		EventType:       "BlockStored",
		PodID:           "prefill-0",
		Role:            "prefill",
		ParentBlockHash: trunk[49],
		BlockHashes:     trunk[50:],
		FreeHBMBlocks:   310,
		Tier:            "dram",
	})

	cfg := scorer.DefaultConfig()
	cfg.Policy = scorer.PolicyFleetKVFit
	cfg.Pool = scorer.PoolDisagg
	eng := scorer.NewEngine(cfg, idx, tel)

	decodeCounts := map[string]int{}
	var leases []scorer.RouteDecision
	defer func() {
		for i := range leases {
			leases[i].Release()
		}
	}()

	for b := 0; b < 8; b++ {
		branchHashes := append([]string{}, trunk...)
		branchHashes = append(branchHashes, fmt.Sprintf("delta_a_%d", b), fmt.Sprintf("delta_b_%d", b))
		dec := eng.Route(scorer.RouteInput{
			RequestID:   fmt.Sprintf("disagg-%d", b),
			BlockHashes: branchHashes,
			TotalTokens: len(branchHashes) * 256,
			MaxTokens:   64,
		})
		leases = append(leases, dec)

		if dec.PrefillPodID != "prefill-0" || dec.PrefillEndpoint != "127.0.0.1:8003" {
			t.Fatalf("expected prefill-0 (127.0.0.1:8003), got pod=%s ep=%s", dec.PrefillPodID, dec.PrefillEndpoint)
		}
		if dec.MatchedHBMBlocks != 50 || dec.MatchedDRAMBlocks != 30 {
			t.Fatalf("expected 50 HBM + 30 DRAM matched blocks, got hbm=%d dram=%d", dec.MatchedHBMBlocks, dec.MatchedDRAMBlocks)
		}
		if dec.TargetEndpoint != dec.DecodeEndpoint {
			t.Fatalf("expected TargetEndpoint (%s) == DecodeEndpoint (%s)", dec.TargetEndpoint, dec.DecodeEndpoint)
		}
		decodeCounts[dec.DecodePodID]++
	}

	if decodeCounts["decode-0"] != 4 || decodeCounts["decode-1"] != 4 {
		t.Fatalf("expected 8 concurrent branches balanced 4/4 across decode-0 and decode-1, got %+v", decodeCounts)
	}
}
