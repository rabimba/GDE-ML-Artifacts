// Copyright 2026 Rabimba Karanjai & Contributors.
// Licensed under the Apache License, Version 2.0.

package extproc

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"log"
	"net/http"
	"strconv"
	"strings"
	"time"

	corev3 "github.com/envoyproxy/go-control-plane/envoy/config/core/v3"
	extprocv3 "github.com/envoyproxy/go-control-plane/envoy/service/ext_proc/v3"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"

	"github.com/rkaranjai/kubecon26-fleetkv-gke/router/pkg/hash"
	"github.com/rkaranjai/kubecon26-fleetkv-gke/router/pkg/metrics"
	"github.com/rkaranjai/kubecon26-fleetkv-gke/router/pkg/radix"
	"github.com/rkaranjai/kubecon26-fleetkv-gke/router/pkg/scorer"
)

const (
	HeaderTargetEndpoint  = "x-gateway-destination-endpoint"
	HeaderPrefillPeer     = "x-fleetkv-prefill-peer"
	HeaderPrefillEndpoint = "x-fleetkv-prefill-endpoint"
	HeaderDecodeEndpoint  = "x-fleetkv-decode-endpoint"
	HeaderSelectedPod     = "x-fleetkv-selected-pod"
	HeaderPolicy          = "x-fleetkv-policy"
	HeaderReason          = "x-fleetkv-reason"
	HeaderMatchedBlocks   = "x-fleetkv-matched-blocks"

	HeaderBranchHorizonHint = "x-branch-horizon-hint"
	HeaderStageOverride     = "x-fleetkv-stage"
	HeaderRequestID         = "x-request-id"
)

// Server implements Envoy's v3 ExternalProcessor gRPC service and the FleetKV Admin HTTP API.
type Server struct {
	extprocv3.UnimplementedExternalProcessorServer

	engine    *scorer.Engine
	index     *radix.ClusterIndex
	telemetry *metrics.Telemetry
	blockSize int
	hashSeed  uint64
	logger    *log.Logger
}

// NewServer creates a FleetKV ExternalProcessor server.
func NewServer(
	engine *scorer.Engine,
	index *radix.ClusterIndex,
	telemetry *metrics.Telemetry,
	blockSize int,
	hashSeed uint64,
	logger *log.Logger,
) *Server {
	if blockSize <= 0 {
		blockSize = hash.DefaultBlockSize
	}
	if telemetry == nil {
		telemetry = metrics.NewTelemetry()
	}
	return &Server{
		engine:    engine,
		index:     index,
		telemetry: telemetry,
		blockSize: blockSize,
		hashSeed:  hashSeed,
		logger:    logger,
	}
}

func extractHeaderValue(h *corev3.HeaderValue) string {
	if h == nil {
		return ""
	}
	if len(h.RawValue) > 0 {
		return string(h.RawValue)
	}
	return h.Value
}

func makeSetHeader(key, val string) *corev3.HeaderValueOption {
	return &corev3.HeaderValueOption{
		Header: &corev3.HeaderValue{
			Key:      key,
			RawValue: []byte(val),
		},
		AppendAction: corev3.HeaderValueOption_OVERWRITE_IF_EXISTS_OR_ADD,
	}
}

func buildRoutingHeaderMutation(dec scorer.RouteDecision) *extprocv3.HeaderMutation {
	opts := []*corev3.HeaderValueOption{
		makeSetHeader(HeaderPolicy, dec.Policy),
		makeSetHeader(HeaderReason, dec.Reason),
		makeSetHeader(HeaderMatchedBlocks, strconv.Itoa(dec.MatchedHBMBlocks+dec.MatchedDRAMBlocks)),
	}

	var removeHeaders []string
	if !dec.Passthrough && dec.TargetEndpoint != "" {
		opts = append(opts,
			makeSetHeader(HeaderTargetEndpoint, dec.TargetEndpoint),
			makeSetHeader(HeaderSelectedPod, dec.SelectedPodID),
		)
		if dec.PrefillEndpoint != "" {
			opts = append(opts,
				makeSetHeader(HeaderPrefillPeer, dec.PrefillEndpoint),
				makeSetHeader(HeaderPrefillEndpoint, dec.PrefillEndpoint),
			)
		} else {
			removeHeaders = append(removeHeaders, HeaderPrefillPeer, HeaderPrefillEndpoint)
		}
		if dec.DecodeEndpoint != "" {
			opts = append(opts, makeSetHeader(HeaderDecodeEndpoint, dec.DecodeEndpoint))
		} else {
			removeHeaders = append(removeHeaders, HeaderDecodeEndpoint)
		}
	} else {
		// Ensure client-supplied target headers cannot spoof upstream routing in round_robin mode.
		removeHeaders = append(removeHeaders,
			HeaderTargetEndpoint,
			HeaderPrefillPeer,
			HeaderPrefillEndpoint,
			HeaderDecodeEndpoint,
		)
	}

	return &extprocv3.HeaderMutation{
		SetHeaders:    opts,
		RemoveHeaders: removeHeaders,
	}
}

func buildResponseHeaderMutation(dec *scorer.RouteDecision) *extprocv3.HeaderMutation {
	if dec == nil {
		return &extprocv3.HeaderMutation{}
	}
	opts := []*corev3.HeaderValueOption{
		makeSetHeader(HeaderPolicy, dec.Policy),
		makeSetHeader(HeaderReason, dec.Reason),
		makeSetHeader(HeaderMatchedBlocks, strconv.Itoa(dec.MatchedHBMBlocks+dec.MatchedDRAMBlocks)),
	}
	if dec.SelectedPodID != "" {
		opts = append(opts, makeSetHeader(HeaderSelectedPod, dec.SelectedPodID))
	}
	if dec.PrefillEndpoint != "" {
		opts = append(opts, makeSetHeader(HeaderPrefillEndpoint, dec.PrefillEndpoint))
	}
	if dec.DecodeEndpoint != "" {
		opts = append(opts, makeSetHeader(HeaderDecodeEndpoint, dec.DecodeEndpoint))
	}
	return &extprocv3.HeaderMutation{SetHeaders: opts}
}

// Process handles bidirectional Envoy ext_proc streams for HTTP inference requests.
func (s *Server) Process(stream extprocv3.ExternalProcessor_ProcessServer) error {
	ctx := stream.Context()

	var (
		reqPath           string
		reqID             string
		stageOverride     string
		horizonHintTokens int
		bodyBuf           bytes.Buffer
		activeDecision    *scorer.RouteDecision
		leaseTimer        *time.Timer
	)

	defer func() {
		if leaseTimer != nil {
			leaseTimer.Stop()
		}
		if activeDecision != nil {
			activeDecision.Release()
		}
	}()

	routeFromPayload := func(payload []byte) scorer.RouteDecision {
		parsed, err := hash.HashChatCompletionsJSON(payload, s.blockSize, s.hashSeed)
		var hashes []string
		totalToks := 0
		maxToks := 64
		if err == nil && parsed != nil {
			hashes = parsed.BlockHashes
			totalToks = parsed.TotalTokens
			maxToks = parsed.MaxTokens
		} else if len(payload) > 0 {
			hashes, totalToks = hash.HashText(string(payload), s.blockSize, s.hashSeed)
		}

		dec := s.engine.Route(scorer.RouteInput{
			RequestID:               reqID,
			BlockHashes:             hashes,
			TotalTokens:             totalToks,
			MaxTokens:               maxToks,
			BranchHorizonHintTokens: horizonHintTokens,
			StageOverride:           stageOverride,
		})
		activeDecision = &dec
		leaseTimer = time.AfterFunc(30*time.Second, func() {
			dec.Release()
		})

		if s.logger != nil {
			s.logger.Printf(
				"[ext_proc] policy=%s pool=%s pod=%s target=%s prefill=%s matched=%d/%d est_blk=%d reason=%s spill=%v",
				dec.Policy,
				dec.Pool,
				dec.SelectedPodID,
				dec.TargetEndpoint,
				dec.PrefillPodID,
				dec.MatchedHBMBlocks+dec.MatchedDRAMBlocks,
				dec.TotalPromptBlocks,
				dec.EstimatedBranchBlocks,
				dec.Reason,
				dec.Spillover,
			)
		}
		return dec
	}

	for {
		select {
		case <-ctx.Done():
			return ctx.Err()
		default:
		}

		req, err := stream.Recv()
		if errors.Is(err, io.EOF) {
			return nil
		}
		if err != nil {
			if status.Code(err) == codes.Canceled || errors.Is(err, context.Canceled) {
				return nil
			}
			return err
		}

		var resp *extprocv3.ProcessingResponse

		switch v := req.Request.(type) {
		case *extprocv3.ProcessingRequest_RequestHeaders:
			if v.RequestHeaders != nil && v.RequestHeaders.Headers != nil {
				for _, h := range v.RequestHeaders.Headers.Headers {
					k := strings.ToLower(h.Key)
					val := extractHeaderValue(h)
					switch k {
					case ":path":
						reqPath = val
					case HeaderRequestID:
						reqID = val
					case HeaderStageOverride:
						stageOverride = val
					case HeaderBranchHorizonHint:
						if parsedHint, convErr := strconv.Atoi(strings.TrimSpace(val)); convErr == nil && parsedHint > 0 {
							horizonHintTokens = parsedHint
						}
					}
				}
			}
			if reqID == "" {
				reqID = fmt.Sprintf("req-%d", time.Now().UnixNano())
			}

			// Non-completion endpoints or bodyless requests bypass body hashing immediately.
			if (reqPath != "" && !strings.HasPrefix(reqPath, "/v1/")) ||
				(v.RequestHeaders != nil && v.RequestHeaders.EndOfStream) {
				if strings.HasPrefix(reqPath, "/v1/") {
					dec := routeFromPayload(nil)
					resp = &extprocv3.ProcessingResponse{
						Response: &extprocv3.ProcessingResponse_RequestHeaders{
							RequestHeaders: &extprocv3.HeadersResponse{
								Response: &extprocv3.CommonResponse{
									HeaderMutation:  buildRoutingHeaderMutation(dec),
									ClearRouteCache: true,
								},
							},
						},
					}
				} else {
					resp = &extprocv3.ProcessingResponse{
						Response: &extprocv3.ProcessingResponse_RequestHeaders{
							RequestHeaders: &extprocv3.HeadersResponse{},
						},
					}
				}
			} else {
				// Acknowledge headers so Envoy buffers and delivers RequestBody before upstream routing.
				resp = &extprocv3.ProcessingResponse{
					Response: &extprocv3.ProcessingResponse_RequestHeaders{
						RequestHeaders: &extprocv3.HeadersResponse{},
					},
				}
			}

		case *extprocv3.ProcessingRequest_RequestBody:
			if v.RequestBody != nil {
				_, _ = bodyBuf.Write(v.RequestBody.Body)
				if !v.RequestBody.EndOfStream {
					resp = &extprocv3.ProcessingResponse{
						Response: &extprocv3.ProcessingResponse_RequestBody{
							RequestBody: &extprocv3.BodyResponse{},
						},
					}
				} else {
					dec := routeFromPayload(bodyBuf.Bytes())
					resp = &extprocv3.ProcessingResponse{
						Response: &extprocv3.ProcessingResponse_RequestBody{
							RequestBody: &extprocv3.BodyResponse{
								Response: &extprocv3.CommonResponse{
									HeaderMutation:  buildRoutingHeaderMutation(dec),
									ClearRouteCache: true,
								},
							},
						},
					}
				}
			} else {
				resp = &extprocv3.ProcessingResponse{
					Response: &extprocv3.ProcessingResponse_RequestBody{
						RequestBody: &extprocv3.BodyResponse{},
					},
				}
			}

		case *extprocv3.ProcessingRequest_ResponseHeaders:
			resp = &extprocv3.ProcessingResponse{
				Response: &extprocv3.ProcessingResponse_ResponseHeaders{
					ResponseHeaders: &extprocv3.HeadersResponse{
						Response: &extprocv3.CommonResponse{
							HeaderMutation: buildResponseHeaderMutation(activeDecision),
						},
					},
				},
			}

		case *extprocv3.ProcessingRequest_ResponseBody:
			if v.ResponseBody != nil && v.ResponseBody.EndOfStream && activeDecision != nil {
				activeDecision.Release()
			}
			resp = &extprocv3.ProcessingResponse{
				Response: &extprocv3.ProcessingResponse_ResponseBody{
					ResponseBody: &extprocv3.BodyResponse{},
				},
			}

		case *extprocv3.ProcessingRequest_RequestTrailers:
			resp = &extprocv3.ProcessingResponse{
				Response: &extprocv3.ProcessingResponse_RequestTrailers{
					RequestTrailers: &extprocv3.TrailersResponse{},
				},
			}

		case *extprocv3.ProcessingRequest_ResponseTrailers:
			if activeDecision != nil {
				activeDecision.Release()
			}
			resp = &extprocv3.ProcessingResponse{
				Response: &extprocv3.ProcessingResponse_ResponseTrailers{
					ResponseTrailers: &extprocv3.TrailersResponse{},
				},
			}
		}

		if resp != nil {
			if err := stream.Send(resp); err != nil {
				return err
			}
		}
	}
}

// NewAdminMux wires /metrics, /healthz, /admin/state, and POST /admin/policy.
func (s *Server) NewAdminMux() *http.ServeMux {
	mux := http.NewServeMux()
	mux.Handle("/metrics", s.telemetry.Handler())

	mux.HandleFunc("/healthz", func(w http.ResponseWriter, _ *http.Request) {
		cfg := s.engine.GetConfig()
		w.Header().Set("Content-Type", "application/json")
		_ = json.NewEncoder(w).Encode(map[string]any{
			"status":         "ok",
			"policy":         cfg.Policy,
			"pool":           cfg.Pool,
			"indexed_blocks": s.index.TotalIndexedBlocks(),
			"pods":           len(s.index.SnapshotPods()),
		})
	})

	mux.HandleFunc("/admin/state", func(w http.ResponseWriter, _ *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		_ = json.NewEncoder(w).Encode(map[string]any{
			"config":           s.engine.GetConfig(),
			"indexed_blocks":   s.index.TotalIndexedBlocks(),
			"pods":             s.index.SnapshotPods(),
			"recent_decisions": s.engine.RecentDecisions(25),
		})
	})

	mux.HandleFunc("/admin/policy", func(w http.ResponseWriter, r *http.Request) {
		if r.Method == http.MethodGet {
			w.Header().Set("Content-Type", "application/json")
			_ = json.NewEncoder(w).Encode(s.engine.GetConfig())
			return
		}
		if r.Method != http.MethodPost {
			http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
			return
		}
		var body struct {
			Policy string `json:"policy"`
			Pool   string `json:"pool"`
		}
		if err := json.NewDecoder(r.Body).Decode(&body); err != nil {
			http.Error(w, fmt.Sprintf("invalid json: %v", err), http.StatusBadRequest)
			return
		}
		if err := s.engine.UpdatePolicy(body.Policy, body.Pool); err != nil {
			http.Error(w, err.Error(), http.StatusBadRequest)
			return
		}
		updated := s.engine.GetConfig()
		if s.logger != nil {
			s.logger.Printf("[admin] hot-reloaded policy=%s pool=%s", updated.Policy, updated.Pool)
		}
		w.Header().Set("Content-Type", "application/json")
		_ = json.NewEncoder(w).Encode(map[string]any{
			"status": "updated",
			"policy": updated.Policy,
			"pool":   updated.Pool,
		})
	})

	mux.HandleFunc("/admin/reset", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
			return
		}
		s.index.ClearBlocks()
		w.Header().Set("Content-Type", "application/json")
		_ = json.NewEncoder(w).Encode(map[string]string{"status": "reset"})
	})

	return mux
}
