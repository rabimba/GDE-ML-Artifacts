// Copyright 2026 Rabimba Karanjai & Contributors.
// Licensed under the Apache License, Version 2.0.

package hash_test

import (
	"encoding/json"
	"fmt"
	"os/exec"
	"path/filepath"
	"strings"
	"testing"

	"github.com/rkaranjai/kubecon26-fleetkv-gke/router/pkg/hash"
)

func buildDeterministicPrompt(numWords int, prefix string) string {
	var sb strings.Builder
	for i := 0; i < numWords; i++ {
		if i > 0 {
			sb.WriteByte(' ')
		}
		fmt.Fprintf(&sb, "%s_%05d", prefix, i)
	}
	return sb.String()
}

func TestChainedPrefixSharingAndDivergence(t *testing.T) {
	trunkText := buildDeterministicPrompt(20480, "mcp_ast")
	branchAText := trunkText + " " + buildDeterministicPrompt(1024, "log_pod_a")
	branchBText := trunkText + " " + buildDeterministicPrompt(1024, "git_diff_b")

	hashesA, toksA := hash.HashText(branchAText, 256, 0)
	hashesB, toksB := hash.HashText(branchBText, 256, 0)

	if toksA != 21504 || toksB != 21504 {
		t.Fatalf("expected 21504 tokens, got A=%d B=%d", toksA, toksB)
	}
	if len(hashesA) != 84 || len(hashesB) != 84 {
		t.Fatalf("expected 84 blocks, got A=%d B=%d", len(hashesA), len(hashesB))
	}

	// First 80 blocks (20,480-token shared trunk) MUST match identically.
	for i := 0; i < 80; i++ {
		if hashesA[i] != hashesB[i] {
			t.Fatalf("trunk block %d diverged: %s vs %s", i, hashesA[i], hashesB[i])
		}
	}
	// Diverging branch suffix blocks 80..83 MUST differ and remain chained.
	for i := 80; i < 84; i++ {
		if hashesA[i] == hashesB[i] {
			t.Fatalf("branch block %d unexpectedly collided: %s", i, hashesA[i])
		}
	}
}

func TestCrossLanguageParityWithPythonTwin(t *testing.T) {
	trunk := buildDeterministicPrompt(2048, "sre_trunk_tok")
	longSubword := "kubectl_crashloop_container_state_abcdefghijklmnop_0123456789"
	payloadMap := map[string]any{
		"model": "Qwen/Qwen3-30B-A3B-FP8",
		"messages": []map[string]any{
			{"role": "system", "content": trunk},
			{"role": "user", "content": longSubword + " " + buildDeterministicPrompt(600, "branch_delta")},
		},
		"max_tokens": 32,
		"stream":     true,
	}
	payloadBytes, err := json.Marshal(payloadMap)
	if err != nil {
		t.Fatalf("marshal payload: %v", err)
	}

	goRes, err := hash.HashChatCompletionsJSON(payloadBytes, 256, 0)
	if err != nil {
		t.Fatalf("HashChatCompletionsJSON failed: %v", err)
	}
	if len(goRes.BlockHashes) < 10 {
		t.Fatalf("expected >= 10 blocks, got %d", len(goRes.BlockHashes))
	}

	twinDir, err := filepath.Abs(filepath.Join("..", "..", "..", "twin"))
	if err != nil {
		t.Fatalf("resolve twin dir: %v", err)
	}

	pyScript := fmt.Sprintf(`
import json, sys
sys.path.insert(0, %q)
from tpu_worker_twin import hash_chat_completions
payload = json.loads(sys.stdin.read())
hashes, total_toks, tail_toks, max_toks = hash_chat_completions(payload, block_size=256, seed=0)
print(json.dumps({"hashes": hashes, "total_tokens": total_toks, "tail_tokens": tail_toks, "max_tokens": max_toks}))
`, twinDir)

	cmd := exec.Command("python3", "-c", pyScript)
	cmd.Env = append(cmd.Environ(), "PYTHONHASHSEED=0")
	cmd.Stdin = strings.NewReader(string(payloadBytes))
	out, err := cmd.CombinedOutput()
	if err != nil {
		t.Fatalf("python parity check failed: %v\noutput: %s", err, string(out))
	}

	var pyRes struct {
		Hashes      []string `json:"hashes"`
		TotalTokens int      `json:"total_tokens"`
		TailTokens  int      `json:"tail_tokens"`
		MaxTokens   int      `json:"max_tokens"`
	}
	if err := json.Unmarshal(out, &pyRes); err != nil {
		t.Fatalf("unmarshal python result: %v (raw=%s)", err, string(out))
	}

	if goRes.TotalTokens != pyRes.TotalTokens {
		t.Fatalf("token count mismatch: Go=%d Python=%d", goRes.TotalTokens, pyRes.TotalTokens)
	}
	if len(goRes.BlockHashes) != len(pyRes.Hashes) {
		t.Fatalf("block count mismatch: Go=%d Python=%d", len(goRes.BlockHashes), len(pyRes.Hashes))
	}
	for i := range goRes.BlockHashes {
		if goRes.BlockHashes[i] != pyRes.Hashes[i] {
			t.Fatalf("block[%d] hash mismatch: Go=%s Python=%s", i, goRes.BlockHashes[i], pyRes.Hashes[i])
		}
	}
}
