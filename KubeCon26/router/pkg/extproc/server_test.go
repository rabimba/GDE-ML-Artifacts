// Copyright 2026 Rabimba Karanjai & Contributors.
// Licensed under the Apache License, Version 2.0.

package extproc_test

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	corev3 "github.com/envoyproxy/go-control-plane/envoy/config/core/v3"
	extprocv3 "github.com/envoyproxy/go-control-plane/envoy/service/ext_proc/v3"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"

	"github.com/rkaranjai/kubecon26-fleetkv-gke/router/pkg/extproc"
	"github.com/rkaranjai/kubecon26-fleetkv-gke/router/pkg/hash"
	"github.com/rkaranjai/kubecon26-fleetkv-gke/router/pkg/metrics"
	"github.com/rkaranjai/kubecon26-fleetkv-gke/router/pkg/radix"
	"github.com/rkaranjai/kubecon26-fleetkv-gke/router/pkg/scorer"
)

func TestExtProcGRPCStreamAndPolicyHotReload(t *testing.T) {
	tel := metrics.NewTelemetry()
	idx := radix.NewClusterIndex(tel)
	idx.UpsertStaticPod("prefill-0", "127.0.0.1:8003", "prefill", 360)
	idx.UpsertStaticPod("decode-0", "127.0.0.1:8004", "decode", 360)

	var promptWords []string
	for i := 0; i < 600; i++ {
		promptWords = append(promptWords, fmt.Sprintf("tok_%04d", i))
	}
	payloadMap := map[string]any{
		"model": "Qwen/Qwen3-30B-A3B-FP8",
		"messages": []map[string]string{
			{"role": "system", "content": strings.Join(promptWords, " ")},
		},
		"max_tokens": 32,
	}
	payloadBytes, _ := json.Marshal(payloadMap)
	parsed, err := hash.HashChatCompletionsJSON(payloadBytes, 256, 0)
	if err != nil {
		t.Fatalf("hash payload: %v", err)
	}

	_ = idx.ApplyEvent(radix.KVEvent{
		EventType:     "BlockStored",
		PodID:         "prefill-0",
		Role:          "prefill",
		BlockHashes:   parsed.BlockHashes,
		FreeHBMBlocks: 350,
		Tier:          "hbm",
	})

	cfg := scorer.DefaultConfig()
	cfg.Policy = scorer.PolicyRoundRobin
	cfg.Pool = scorer.PoolAgg
	eng := scorer.NewEngine(cfg, idx, tel)

	srv := extproc.NewServer(eng, idx, tel, 256, 0, nil)
	adminTS := httptest.NewServer(srv.NewAdminMux())
	defer adminTS.Close()

	lis, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		t.Fatalf("listen grpc: %v", err)
	}
	grpcServer := grpc.NewServer()
	extprocv3.RegisterExternalProcessorServer(grpcServer, srv)
	go func() { _ = grpcServer.Serve(lis) }()
	defer grpcServer.Stop()

	// Hot-reload from round_robin -> fleetkv_fit + disagg via HTTP POST /admin/policy
	reloadBody := bytes.NewBufferString(`{"policy":"fleetkv_fit","pool":"disagg"}`)
	httpResp, err := http.Post(adminTS.URL+"/admin/policy", "application/json", reloadBody)
	if err != nil || httpResp.StatusCode != http.StatusOK {
		t.Fatalf("POST /admin/policy failed: err=%v status=%v", err, httpResp)
	}
	_ = httpResp.Body.Close()

	conn, err := grpc.NewClient(lis.Addr().String(), grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		t.Fatalf("dial grpc: %v", err)
	}
	defer func() { _ = conn.Close() }()

	client := extprocv3.NewExternalProcessorClient(conn)
	stream, err := client.Process(context.Background())
	if err != nil {
		t.Fatalf("open Process stream: %v", err)
	}

	// 1. Send RequestHeaders
	err = stream.Send(&extprocv3.ProcessingRequest{
		Request: &extprocv3.ProcessingRequest_RequestHeaders{
			RequestHeaders: &extprocv3.HttpHeaders{
				Headers: &corev3.HeaderMap{
					Headers: []*corev3.HeaderValue{
						{Key: ":path", RawValue: []byte("/v1/chat/completions")},
						{Key: "x-request-id", RawValue: []byte("test-req-1")},
						{Key: "x-branch-horizon-hint", RawValue: []byte("1024")},
					},
				},
				EndOfStream: false,
			},
		},
	})
	if err != nil {
		t.Fatalf("send RequestHeaders: %v", err)
	}
	if _, err := stream.Recv(); err != nil {
		t.Fatalf("recv RequestHeaders ack: %v", err)
	}

	// 2. Send multi-chunk RequestBody (chunk 1 with EndOfStream=false, chunk 2 with EndOfStream=true)
	mid := len(payloadBytes) / 2
	err = stream.Send(&extprocv3.ProcessingRequest{
		Request: &extprocv3.ProcessingRequest_RequestBody{
			RequestBody: &extprocv3.HttpBody{
				Body:        payloadBytes[:mid],
				EndOfStream: false,
			},
		},
	})
	if err != nil {
		t.Fatalf("send RequestBody chunk 1: %v", err)
	}
	if _, err := stream.Recv(); err != nil {
		t.Fatalf("recv RequestBody chunk 1 ack: %v", err)
	}

	err = stream.Send(&extprocv3.ProcessingRequest{
		Request: &extprocv3.ProcessingRequest_RequestBody{
			RequestBody: &extprocv3.HttpBody{
				Body:        payloadBytes[mid:],
				EndOfStream: true,
			},
		},
	})
	if err != nil {
		t.Fatalf("send RequestBody chunk 2: %v", err)
	}

	bodyResp, err := stream.Recv()
	if err != nil {
		t.Fatalf("recv RequestBody response: %v", err)
	}
	br := bodyResp.GetRequestBody()
	if br == nil || br.Response == nil || !br.Response.ClearRouteCache {
		t.Fatalf("expected ClearRouteCache=true in BodyResponse, got %+v", bodyResp)
	}

	mutated := map[string]string{}
	for _, h := range br.Response.HeaderMutation.SetHeaders {
		mutated[h.Header.Key] = string(h.Header.RawValue)
	}
	if mutated[extproc.HeaderTargetEndpoint] != "127.0.0.1:8004" {
		t.Fatalf("expected x-gateway-destination-endpoint=127.0.0.1:8004, got %q", mutated[extproc.HeaderTargetEndpoint])
	}
	if mutated[extproc.HeaderPrefillPeer] != "127.0.0.1:8003" {
		t.Fatalf("expected x-fleetkv-prefill-peer=127.0.0.1:8003, got %q", mutated[extproc.HeaderPrefillPeer])
	}
	if mutated[extproc.HeaderDecodeEndpoint] != "127.0.0.1:8004" {
		t.Fatalf("expected x-fleetkv-decode-endpoint=127.0.0.1:8004, got %q", mutated[extproc.HeaderDecodeEndpoint])
	}

	// 3. Send ResponseHeaders and verify in-flight prefill reservation is released while decode stays active
	err = stream.Send(&extprocv3.ProcessingRequest{
		Request: &extprocv3.ProcessingRequest_ResponseHeaders{
			ResponseHeaders: &extprocv3.HttpHeaders{},
		},
	})
	if err != nil {
		t.Fatalf("send ResponseHeaders: %v", err)
	}
	if _, err := stream.Recv(); err != nil {
		t.Fatalf("recv ResponseHeaders response: %v", err)
	}
	for _, p := range idx.SnapshotPods() {
		if p.PodID == "prefill-0" && p.InFlightPrefillTokens != 0 {
			t.Fatalf("expected prefill-0 InFlightPrefillTokens=0 after ResponseHeaders, got %d", p.InFlightPrefillTokens)
		}
	}

	_ = stream.CloseSend()

	// Verify /metrics Prometheus exposition contains fleetkv_radix_blocks_total and fleetkv_route_decisions_total
	mResp, err := http.Get(adminTS.URL + "/metrics")
	if err != nil {
		t.Fatalf("GET /metrics: %v", err)
	}
	defer func() { _ = mResp.Body.Close() }()
	mRaw, _ := io.ReadAll(mResp.Body)
	mText := string(mRaw)
	if !strings.Contains(mText, "fleetkv_radix_blocks_total") || !strings.Contains(mText, "fleetkv_route_decisions_total") {
		t.Fatalf("expected Prometheus metrics missing:\n%s", mText)
	}
}
