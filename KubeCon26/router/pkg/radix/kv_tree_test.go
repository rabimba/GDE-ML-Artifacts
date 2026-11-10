// Copyright 2026 Rabimba Karanjai & Contributors.
// Licensed under the Apache License, Version 2.0.

package radix_test

import (
	"fmt"
	"sync"
	"testing"

	"github.com/rkaranjai/kubecon26-fleetkv-gke/router/pkg/radix"
)

func TestRadixInsertEvictAndTier2DRAM(t *testing.T) {
	idx := radix.NewClusterIndex(nil)
	trunk := make([]string, 80)
	for i := range trunk {
		trunk[i] = fmt.Sprintf("%016x", uint64(i+1))
	}

	err := idx.ApplyEvent(radix.KVEvent{
		EventType:         "BlockStored",
		PodID:             "prefill-0",
		IPPort:            "127.0.0.1:8003",
		Role:              "prefill",
		BlockHashes:       trunk,
		FreeHBMBlocks:     280,
		HBMCapacityBlocks: 360,
		Tier:              "hbm",
	})
	if err != nil {
		t.Fatalf("ApplyEvent failed: %v", err)
	}
	if idx.TotalIndexedBlocks() != 80 {
		t.Fatalf("expected 80 indexed blocks, got %d", idx.TotalIndexedBlocks())
	}

	matches := idx.MatchPods(trunk, "prefill")
	if len(matches) != 1 || matches[0].MatchedHBMBlocks != 80 {
		t.Fatalf("expected 80 HBM blocks matched, got %+v", matches)
	}

	// Simulate spilling blocks 40..79 from HBM into Tier-2 Host DRAM via TPUConnectorHMA.
	spilled := trunk[40:]
	_ = idx.ApplyEvent(radix.KVEvent{
		EventType:     "BlockRemoved",
		PodID:         "prefill-0",
		Role:          "prefill",
		BlockHashes:   spilled,
		FreeHBMBlocks: 320,
		Tier:          "hbm",
	})
	_ = idx.ApplyEvent(radix.KVEvent{
		EventType:     "BlockStored",
		PodID:         "prefill-0",
		Role:          "prefill",
		BlockHashes:   spilled,
		FreeHBMBlocks: 320,
		Tier:          "dram",
	})

	matches = idx.MatchPods(trunk, "prefill")
	if matches[0].MatchedHBMBlocks != 40 || matches[0].MatchedDRAMBlocks != 40 {
		t.Fatalf("expected 40 HBM + 40 DRAM blocks matched, got %+v", matches[0])
	}

	// Evict block 20 from both tiers -> breaks contiguous APC prefix at block 20!
	_ = idx.ApplyEvent(radix.KVEvent{
		EventType:     "BlockRemoved",
		PodID:         "prefill-0",
		Role:          "prefill",
		BlockHashes:   []string{trunk[20]},
		FreeHBMBlocks: 321,
		Tier:          "hbm",
	})
	matches = idx.MatchPods(trunk, "prefill")
	if matches[0].TotalMatchedBlocks() != 20 {
		t.Fatalf("expected contiguous prefix broken at 20, got %d", matches[0].TotalMatchedBlocks())
	}
}

func TestConcurrentMutationsAndLeasesRaceFree(t *testing.T) {
	idx := radix.NewClusterIndex(nil)
	idx.UpsertStaticPod("agg-0", "127.0.0.1:8001", "agg", 360)
	idx.UpsertStaticPod("agg-1", "127.0.0.1:8002", "agg", 360)

	var wg sync.WaitGroup
	for g := 0; g < 16; g++ {
		wg.Add(1)
		go func(worker int) {
			defer wg.Done()
			hashes := []string{
				fmt.Sprintf("00000000000000%02x", worker),
				fmt.Sprintf("11111111111111%02x", worker),
			}
			pod := fmt.Sprintf("agg-%d", worker%2)
			_ = idx.ApplyEvent(radix.KVEvent{
				EventType:     "BlockStored",
				PodID:         pod,
				BlockHashes:   hashes,
				FreeHBMBlocks: 300,
				Tier:          "hbm",
			})
			rel := idx.AcquireLease(pod, 8, 2048)
			_ = idx.MatchPods(hashes, "agg")
			rel()
			rel() // verify idempotent release
			_ = idx.ApplyEvent(radix.KVEvent{
				EventType:     "BlockRemoved",
				PodID:         pod,
				BlockHashes:   hashes,
				FreeHBMBlocks: 302,
				Tier:          "hbm",
			})
		}(g)
	}
	wg.Wait()

	for _, p := range idx.SnapshotPods() {
		if p.ReservedBlocks != 0 || p.InFlightPrefillTokens != 0 || p.ActiveRequests != 0 {
			t.Fatalf("expected all leases released cleanly, got %+v", p)
		}
	}
}
