// Copyright 2026 Rabimba Karanjai & Contributors.
// Licensed under the Apache License, Version 2.0.

package extproc

import (
	"bytes"
	"context"
	"fmt"
	"io"
	"net/http"
	"strings"
	"sync"
	"sync/atomic"
	"time"

	corev3 "github.com/envoyproxy/go-control-plane/envoy/config/core/v3"
	extprocv3 "github.com/envoyproxy/go-control-plane/envoy/service/ext_proc/v3"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"

	"github.com/rkaranjai/kubecon26-fleetkv-gke/router/pkg/radix"
)

// GatewayProxy implements an Envoy-compatible HTTP ingress gateway that invokes
// ExternalProcessor over gRPC (RequestHeaders -> RequestBody -> ResponseHeaders),
// routes to x-gateway-destination-endpoint when set (GAIE Endpoint Picker cluster),
// and falls back to round-robin across aggregated pods when unset (Stage 1).
type GatewayProxy struct {
	extProcAddr string
	index       *radix.ClusterIndex
	httpClient  *http.Client
	rrCounter   atomic.Uint64

	connMu      sync.Mutex
	conns       []*grpc.ClientConn
	connCounter atomic.Uint64
}

// NewGatewayProxy creates a new Envoy-compatible ext_proc HTTP gateway proxy.
func NewGatewayProxy(extProcAddr string, index *radix.ClusterIndex) *GatewayProxy {
	return &GatewayProxy{
		extProcAddr: extProcAddr,
		index:       index,
		httpClient: &http.Client{
			Timeout: 300 * time.Second,
			Transport: &http.Transport{
				MaxIdleConns:        512,
				MaxIdleConnsPerHost: 128,
				IdleConnTimeout:     90 * time.Second,
				DisableCompression:  true,
			},
		},
	}
}

func (g *GatewayProxy) getClient() (extprocv3.ExternalProcessorClient, error) {
	const poolSize = 8
	g.connMu.Lock()
	if len(g.conns) == 0 {
		conns := make([]*grpc.ClientConn, 0, poolSize)
		for i := 0; i < poolSize; i++ {
			c, err := grpc.NewClient(
				g.extProcAddr,
				grpc.WithTransportCredentials(insecure.NewCredentials()),
				grpc.WithInitialWindowSize(16*1024*1024),
				grpc.WithInitialConnWindowSize(64*1024*1024),
				grpc.WithDefaultCallOptions(
					grpc.MaxCallRecvMsgSize(32*1024*1024),
					grpc.MaxCallSendMsgSize(32*1024*1024),
				),
			)
			if err != nil {
				g.connMu.Unlock()
				return nil, err
			}
			conns = append(conns, c)
		}
		g.conns = conns
	}
	conns := g.conns
	g.connMu.Unlock()
	idx := int(g.connCounter.Add(1)-1) % len(conns)
	return extprocv3.NewExternalProcessorClient(conns[idx]), nil
}

func applyMutationToHeaders(hdr http.Header, mut *extprocv3.HeaderMutation) {
	if mut == nil {
		return
	}
	for _, rem := range mut.RemoveHeaders {
		hdr.Del(rem)
	}
	for _, opt := range mut.SetHeaders {
		if opt == nil || opt.Header == nil {
			continue
		}
		val := opt.Header.Value
		if len(opt.Header.RawValue) > 0 {
			val = string(opt.Header.RawValue)
		}
		hdr.Set(opt.Header.Key, val)
	}
}

func (g *GatewayProxy) pickRoundRobinAggEndpoint() (string, error) {
	pods := g.index.SnapshotPods()
	agg := make([]string, 0, len(pods))
	for _, p := range pods {
		if p.Role == radix.RoleAgg && p.IPPort != "" {
			agg = append(agg, p.IPPort)
		}
	}
	if len(agg) == 0 {
		for _, p := range pods {
			if p.IPPort != "" {
				agg = append(agg, p.IPPort)
			}
		}
	}
	if len(agg) == 0 {
		return "", fmt.Errorf("no backend pods registered in cluster index")
	}
	idx := int(g.rrCounter.Add(1)-1) % len(agg)
	return agg[idx], nil
}

// ServeHTTP handles incoming HTTP requests through the ext_proc gRPC filter pipeline.
func (g *GatewayProxy) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()

	bodyBytes, err := io.ReadAll(r.Body)
	if err != nil {
		http.Error(w, fmt.Sprintf("read request body: %v", err), http.StatusBadRequest)
		return
	}
	_ = r.Body.Close()

	client, err := g.getClient()
	if err != nil {
		http.Error(w, fmt.Sprintf("dial ext_proc: %v", err), http.StatusBadGateway)
		return
	}

	streamCtx, cancelStream := context.WithCancel(ctx)
	defer cancelStream()

	stream, err := client.Process(streamCtx)
	if err != nil {
		http.Error(w, fmt.Sprintf("open ext_proc stream: %v", err), http.StatusBadGateway)
		return
	}
	defer func() { _ = stream.CloseSend() }()

	outHeaders := r.Header.Clone()
	reqPath := r.URL.RequestURI()

	envoyHeaders := []*corev3.HeaderValue{
		{Key: ":path", RawValue: []byte(reqPath)},
		{Key: ":method", RawValue: []byte(r.Method)},
	}
	for k, vals := range r.Header {
		if len(vals) > 0 {
			envoyHeaders = append(envoyHeaders, &corev3.HeaderValue{
				Key:      strings.ToLower(k),
				RawValue: []byte(vals[0]),
			})
		}
	}

	endOfStream := len(bodyBytes) == 0
	if err := stream.Send(&extprocv3.ProcessingRequest{
		Request: &extprocv3.ProcessingRequest_RequestHeaders{
			RequestHeaders: &extprocv3.HttpHeaders{
				Headers:     &corev3.HeaderMap{Headers: envoyHeaders},
				EndOfStream: endOfStream,
			},
		},
	}); err != nil {
		http.Error(w, fmt.Sprintf("send ext_proc RequestHeaders: %v", err), http.StatusBadGateway)
		return
	}

	hdrResp, err := stream.Recv()
	if err != nil {
		http.Error(w, fmt.Sprintf("recv ext_proc RequestHeaders: %v", err), http.StatusBadGateway)
		return
	}
	if rh := hdrResp.GetRequestHeaders(); rh != nil && rh.Response != nil {
		applyMutationToHeaders(outHeaders, rh.Response.HeaderMutation)
	}

	if !endOfStream {
		if err := stream.Send(&extprocv3.ProcessingRequest{
			Request: &extprocv3.ProcessingRequest_RequestBody{
				RequestBody: &extprocv3.HttpBody{
					Body:        bodyBytes,
					EndOfStream: true,
				},
			},
		}); err != nil {
			http.Error(w, fmt.Sprintf("send ext_proc RequestBody: %v", err), http.StatusBadGateway)
			return
		}
		bodyResp, err := stream.Recv()
		if err != nil {
			http.Error(w, fmt.Sprintf("recv ext_proc RequestBody: %v", err), http.StatusBadGateway)
			return
		}
		if rb := bodyResp.GetRequestBody(); rb != nil && rb.Response != nil {
			applyMutationToHeaders(outHeaders, rb.Response.HeaderMutation)
		}
	}

	targetEndpoint := strings.TrimSpace(outHeaders.Get(HeaderTargetEndpoint))
	if targetEndpoint == "" {
		targetEndpoint, err = g.pickRoundRobinAggEndpoint()
		if err != nil {
			http.Error(w, err.Error(), http.StatusServiceUnavailable)
			return
		}
	}

	upstreamURL := fmt.Sprintf("http://%s%s", targetEndpoint, reqPath)
	upReq, err := http.NewRequestWithContext(ctx, r.Method, upstreamURL, bytes.NewReader(bodyBytes))
	if err != nil {
		http.Error(w, fmt.Sprintf("create upstream request: %v", err), http.StatusInternalServerError)
		return
	}
	upReq.Header = outHeaders

	upResp, err := g.httpClient.Do(upReq)
	if err != nil {
		http.Error(w, fmt.Sprintf("upstream request to %s failed: %v", targetEndpoint, err), http.StatusBadGateway)
		return
	}
	defer func() { _ = upResp.Body.Close() }()

	respHeaders := upResp.Header.Clone()
	if err := stream.Send(&extprocv3.ProcessingRequest{
		Request: &extprocv3.ProcessingRequest_ResponseHeaders{
			ResponseHeaders: &extprocv3.HttpHeaders{
				Headers:     &corev3.HeaderMap{},
				EndOfStream: false,
			},
		},
	}); err == nil {
		if extRespHdr, recvErr := stream.Recv(); recvErr == nil {
			if rhr := extRespHdr.GetResponseHeaders(); rhr != nil && rhr.Response != nil {
				applyMutationToHeaders(respHeaders, rhr.Response.HeaderMutation)
			}
		}
	}

	for k, vals := range respHeaders {
		for _, v := range vals {
			w.Header().Add(k, v)
		}
	}
	w.WriteHeader(upResp.StatusCode)

	flusher, canFlush := w.(http.Flusher)
	if canFlush {
		flusher.Flush()
	}
	buf := make([]byte, 4096)
	for {
		n, readErr := upResp.Body.Read(buf)
		if n > 0 {
			if _, writeErr := w.Write(buf[:n]); writeErr != nil {
				break
			}
			if canFlush {
				flusher.Flush()
			}
		}
		if readErr != nil {
			break
		}
	}
}
