// Copyright 2026 Rabimba Karanjai & Contributors.
// Licensed under the Apache License, Version 2.0.

package hash

import (
	"crypto/sha256"
	"encoding/binary"
	"encoding/json"
	"fmt"
	"strings"
	"sync"
)

const (
	// DefaultBlockSize matches TPU v6e Pallas paged-attention --block-size 256.
	DefaultBlockSize = 256
	// DefaultHashSeed matches PYTHONHASHSEED=0 across serving pods and routers.
	DefaultHashSeed uint64 = 0
	// SubwordChunkBytes bounds deterministic subword splitting for long tokens.
	SubwordChunkBytes = 16
)

// MessageContent decodes either a plain JSON string or an OpenAI multimodal content part list.
type MessageContent struct {
	Text string
}

// UnmarshalJSON supports string content or [{"type":"text","text":"..."}] arrays.
func (mc *MessageContent) UnmarshalJSON(data []byte) error {
	trimmed := strings.TrimSpace(string(data))
	if trimmed == "" || trimmed == "null" {
		mc.Text = ""
		return nil
	}
	if trimmed[0] == '"' {
		var s string
		if err := json.Unmarshal(data, &s); err != nil {
			return err
		}
		mc.Text = s
		return nil
	}
	if trimmed[0] == '[' {
		var parts []struct {
			Type string `json:"type"`
			Text string `json:"text"`
		}
		if err := json.Unmarshal(data, &parts); err != nil {
			return err
		}
		var sb strings.Builder
		for i, p := range parts {
			if i > 0 {
				sb.WriteByte('\n')
			}
			sb.WriteString(p.Text)
		}
		mc.Text = sb.String()
		return nil
	}
	return fmt.Errorf("unsupported message content JSON: %s", trimmed)
}

// ChatMessage represents a single OpenAI-compatible chat turn.
type ChatMessage struct {
	Role    string         `json:"role"`
	Content MessageContent `json:"content"`
}

// ChatCompletionRequest captures fields needed by FleetKV block hashing and HBM fit estimation.
type ChatCompletionRequest struct {
	Model               string        `json:"model"`
	Messages            []ChatMessage `json:"messages"`
	Prompt              string        `json:"prompt"`
	MaxTokens           int           `json:"max_tokens"`
	MaxCompletionTokens int           `json:"max_completion_tokens"`
	Stream              bool          `json:"stream"`
}

// PromptHashResult summarizes the deterministic 256-token block hashes of a request.
type PromptHashResult struct {
	Model       string
	BlockHashes []string
	TotalTokens int
	TailTokens  int
	MaxTokens   int
	Stream      bool
}

// CanonicalizeMessages renders chat messages in deterministic ChatML format.
func CanonicalizeMessages(msgs []ChatMessage) string {
	var sb strings.Builder
	for _, m := range msgs {
		sb.WriteString("<|im_start|>")
		sb.WriteString(m.Role)
		sb.WriteByte('\n')
		sb.WriteString(m.Content.Text)
		sb.WriteString("<|im_end|>\n")
	}
	return sb.String()
}

func isASCIIWhitespace(b byte) bool {
	switch b {
	case ' ', '\t', '\n', '\r', '\v', '\f':
		return true
	default:
		return false
	}
}

type alignedSegKey struct {
	parent    uint64
	blockSize int
	tailKey   string
	seg       string
}

type alignedSegVal struct {
	newParent uint64
	hashes    []string
	newTail   [][]byte
	numTokens int
}

func makeTailKey(tokens [][]byte) string {
	if len(tokens) == 0 {
		return ""
	}
	var sb strings.Builder
	for i, t := range tokens {
		if i > 0 {
			sb.WriteByte(0)
		}
		sb.Write(t)
	}
	return sb.String()
}

var alignedSegCache sync.Map

// ClearAlignedCache clears cached aligned segment block hashes.
func ClearAlignedCache() {
	alignedSegCache.Clear()
}

// TokenizeDeterministic splits UTF-8 text on ASCII whitespace and chunks long runs into
// fixed 16-byte subwords. Implemented identically in Python (twin/tpu_worker_twin.py).
func TokenizeDeterministic(text string) [][]byte {
	raw := []byte(text)
	n := len(raw)
	tokens := make([][]byte, 0, n/5+1)
	i := 0
	for i < n {
		for i < n && isASCIIWhitespace(raw[i]) {
			i++
		}
		if i >= n {
			break
		}
		start := i
		for i < n && !isASCIIWhitespace(raw[i]) {
			i++
		}
		word := raw[start:i]
		for j := 0; j < len(word); j += SubwordChunkBytes {
			end := j + SubwordChunkBytes
			if end > len(word) {
				end = len(word)
			}
			tokens = append(tokens, word[j:end])
		}
	}
	return tokens
}

func hashTokensWithParent(tokens [][]byte, blockSize int, seed uint64) ([]string, uint64) {
	if blockSize <= 0 {
		blockSize = DefaultBlockSize
	}
	numBlocks := len(tokens) / blockSize
	if numBlocks == 0 {
		return []string{}, seed
	}

	hashes := make([]string, numBlocks)
	parent := seed
	var headerBuf [12]byte
	var lenBuf [2]byte

	for b := 0; b < numBlocks; b++ {
		h := sha256.New()
		binary.BigEndian.PutUint64(headerBuf[0:8], parent)
		binary.BigEndian.PutUint32(headerBuf[8:12], uint32(blockSize))
		_, _ = h.Write(headerBuf[:])

		start := b * blockSize
		end := start + blockSize
		for _, tok := range tokens[start:end] {
			binary.BigEndian.PutUint16(lenBuf[:], uint16(len(tok)))
			_, _ = h.Write(lenBuf[:])
			_, _ = h.Write(tok)
		}

		digest := h.Sum(nil)
		blockID := binary.BigEndian.Uint64(digest[0:8])
		hashes[b] = fmt.Sprintf("%016x", blockID)
		parent = blockID
	}

	return hashes, parent
}

// ComputeBlockHashes computes chained prefix SHA-256 64-bit hex block identifiers
// over full blockSize-token chunks seeded by seed (0 when PYTHONHASHSEED=0).
func ComputeBlockHashes(tokens [][]byte, blockSize int, seed uint64) []string {
	hashes, _ := hashTokensWithParent(tokens, blockSize, seed)
	return hashes
}

// HashText is a convenience helper combining TokenizeDeterministic and ComputeBlockHashes.
func HashText(text string, blockSize int, seed uint64) ([]string, int) {
	tokens := TokenizeDeterministic(text)
	return ComputeBlockHashes(tokens, blockSize, seed), len(tokens)
}

// HashChatCompletionsJSON parses an OpenAI /v1/chat/completions payload and computes chained block hashes.
func HashChatCompletionsJSON(body []byte, blockSize int, seed uint64) (*PromptHashResult, error) {
	if blockSize <= 0 {
		blockSize = DefaultBlockSize
	}
	var req ChatCompletionRequest
	if err := json.Unmarshal(body, &req); err != nil {
		return nil, fmt.Errorf("invalid chat completions JSON: %w", err)
	}

	var (
		hashes     []string
		tailTokens [][]byte
		totalToks  int
		parent     = seed
	)

	if len(req.Messages) > 0 {
		for _, m := range req.Messages {
			seg := "<|im_start|>" + m.Role + "\n" + m.Content.Text + "<|im_end|>\n"
			key := alignedSegKey{
				parent:    parent,
				blockSize: blockSize,
				tailKey:   makeTailKey(tailTokens),
				seg:       seg,
			}
			if cached, ok := alignedSegCache.Load(key); ok {
				val := cached.(alignedSegVal)
				parent = val.newParent
				hashes = append(hashes, val.hashes...)
				tailTokens = append(tailTokens[:0], val.newTail...)
				totalToks += val.numTokens
				continue
			}

			segToks := TokenizeDeterministic(seg)
			segLen := len(segToks)
			totalToks += segLen
			combined := append(append([][]byte(nil), tailTokens...), segToks...)
			var (
				segHashes []string
				newParent = parent
				remTail   = combined
			)
			if len(combined) >= blockSize {
				nFull := (len(combined) / blockSize) * blockSize
				segHashes, newParent = hashTokensWithParent(combined[:nFull], blockSize, parent)
				remTail = append([][]byte(nil), combined[nFull:]...)
			}
			if segLen >= blockSize {
				alignedSegCache.Store(key, alignedSegVal{
					newParent: newParent,
					hashes:    segHashes,
					newTail:   remTail,
					numTokens: segLen,
				})
			}
			parent = newParent
			hashes = append(hashes, segHashes...)
			tailTokens = remTail
		}
	} else {
		tokens := TokenizeDeterministic(req.Prompt)
		totalToks = len(tokens)
		hashes, _ = hashTokensWithParent(tokens, blockSize, parent)
	}

	maxToks := req.MaxCompletionTokens
	if maxToks <= 0 {
		maxToks = req.MaxTokens
	}
	if maxToks <= 0 {
		maxToks = 64
	}

	return &PromptHashResult{
		Model:       req.Model,
		BlockHashes: hashes,
		TotalTokens: totalToks,
		TailTokens:  totalToks % blockSize,
		MaxTokens:   maxToks,
		Stream:      req.Stream,
	}, nil
}
