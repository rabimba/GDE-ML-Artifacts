// Copyright 2026 Rabimba Karanjai & Contributors.
// Licensed under the Apache License, Version 2.0.

package main

import (
	"context"
	"errors"
	"flag"
	"fmt"
	"log"
	"net"
	"net/http"
	"os"
	"os/signal"
	"strconv"
	"strings"
	"syscall"
	"time"

	extprocv3 "github.com/envoyproxy/go-control-plane/envoy/service/ext_proc/v3"
	"google.golang.org/grpc"
	"google.golang.org/grpc/health"
	healthpb "google.golang.org/grpc/health/grpc_health_v1"

	"github.com/rkaranjai/kubecon26-fleetkv-gke/router/pkg/extproc"
	"github.com/rkaranjai/kubecon26-fleetkv-gke/router/pkg/hash"
	"github.com/rkaranjai/kubecon26-fleetkv-gke/router/pkg/metrics"
	"github.com/rkaranjai/kubecon26-fleetkv-gke/router/pkg/radix"
	"github.com/rkaranjai/kubecon26-fleetkv-gke/router/pkg/scorer"
	"github.com/rkaranjai/kubecon26-fleetkv-gke/router/pkg/zmqsub"
)

func envOrDefault(key, fallback string) string {
	if v := strings.TrimSpace(os.Getenv(key)); v != "" {
		return v
	}
	return fallback
}

func envIntOrDefault(key string, fallback int) int {
	if v := strings.TrimSpace(os.Getenv(key)); v != "" {
		if n, err := strconv.Atoi(v); err == nil {
			return n
		}
	}
	return fallback
}

// parseStaticPods parses entries formatted as "podID=host:port:role[:capacity]" separated by commas.
func parseStaticPods(spec string, index *radix.ClusterIndex, logger *log.Logger) {
	for _, item := range strings.Split(spec, ",") {
		item = strings.TrimSpace(item)
		if item == "" {
			continue
		}
		eq := strings.SplitN(item, "=", 2)
		if len(eq) != 2 {
			logger.Printf("[init] ignoring malformed --static-pods entry %q", item)
			continue
		}
		podID := strings.TrimSpace(eq[0])
		parts := strings.Split(eq[1], ":")
		if len(parts) < 3 {
			logger.Printf("[init] ignoring malformed --static-pods target %q", eq[1])
			continue
		}
		ipPort := parts[0] + ":" + parts[1]
		role := parts[2]
		capBlocks := 360
		if len(parts) >= 4 {
			if n, err := strconv.Atoi(parts[3]); err == nil && n > 0 {
				capBlocks = n
			}
		}
		index.UpsertStaticPod(podID, ipPort, role, capBlocks)
		logger.Printf("[init] registered static pod id=%s endpoint=%s role=%s hbm_blocks=%d", podID, ipPort, role, capBlocks)
	}
}

func parseAllowedRoles(selector string) map[string]bool {
	selector = strings.TrimSpace(selector)
	if selector == "" {
		return nil
	}
	// Support K8s label selector format e.g. "llm-d.ai/role=prefill" or comma-separated roles "prefill,decode,agg".
	if strings.Contains(selector, "=") {
		kv := strings.SplitN(selector, "=", 2)
		selector = kv[1]
	}
	roles := make(map[string]bool)
	for _, r := range strings.Split(selector, ",") {
		r = strings.ToLower(strings.TrimSpace(r))
		if r != "" {
			roles[r] = true
		}
	}
	if len(roles) == 0 {
		return nil
	}
	return roles
}

func main() {
	var (
		grpcPort            = flag.Int("grpc-port", envIntOrDefault("FLEETKV_GRPC_PORT", 9002), "Envoy ext_proc gRPC listen port")
		metricsPort         = flag.Int("metrics-port", envIntOrDefault("FLEETKV_METRICS_PORT", 9090), "Prometheus metrics & admin HTTP listen port")
		policy              = flag.String("policy", envOrDefault("FLEETKV_POLICY", scorer.PolicyFleetKVFit), "Initial routing policy: round_robin | naive_sticky | fleetkv_fit")
		pool                = flag.String("pool", envOrDefault("FLEETKV_POOL", scorer.PoolAuto), "Active pool mode: auto | agg | disagg")
		blockSize           = flag.Int("block-size", envIntOrDefault("FLEETKV_BLOCK_SIZE", hash.DefaultBlockSize), "Deterministic KV block size in tokens (must match vLLM --block-size 256)")
		safetyReserveBlocks = flag.Int("safety-reserve-blocks", envIntOrDefault("FLEETKV_SAFETY_RESERVE_BLOCKS", 24), "HBM safety reserve blocks for Fit Admission Gate")
		peakPrefillTokens   = flag.Int("peak-prefill-tokens", envIntOrDefault("FLEETKV_PEAK_PREFILL_TOKENS", 12288), "Max in-flight prefill tokens per pod before spillover")
		zmqEndpoints        = flag.String("zmq-endpoints", envOrDefault("FLEETKV_ZMQ_ENDPOINTS", ""), "Comma-separated ZeroMQ PUB endpoints (e.g. tcp://127.0.0.1:5557)")
		zmqTopic            = flag.String("zmq-topic", envOrDefault("FLEETKV_ZMQ_TOPIC", ""), "ZeroMQ subscription prefix")
		zmqRoleSelector     = flag.String("zmq-role-selector", envOrDefault("FLEETKV_ZMQ_ROLE_SELECTOR", ""), "Optional ZMQ role filter (e.g. llm-d.ai/role=prefill)")
		staticPods          = flag.String("static-pods", envOrDefault("FLEETKV_STATIC_PODS", ""), "Comma-separated static pod specs podID=host:port:role[:hbm_blocks]")
	)
	flag.Parse()

	logger := log.New(os.Stdout, "[fleetkv-epp] ", log.LstdFlags|log.Lmicroseconds)

	hashSeed := hash.DefaultHashSeed
	if rawSeed := strings.TrimSpace(os.Getenv("PYTHONHASHSEED")); rawSeed != "" {
		if parsed, err := strconv.ParseUint(rawSeed, 10, 64); err == nil {
			hashSeed = parsed
		}
	}

	telemetry := metrics.NewTelemetry()
	index := radix.NewClusterIndex(telemetry)

	if *staticPods != "" {
		parseStaticPods(*staticPods, index, logger)
	}

	cfg := scorer.DefaultConfig()
	cfg.Policy = *policy
	cfg.Pool = *pool
	cfg.BlockSizeTokens = *blockSize
	cfg.SafetyReserveBlocks = *safetyReserveBlocks
	cfg.PeakPrefillThresholdTokens = *peakPrefillTokens

	engine := scorer.NewEngine(cfg, index, telemetry)
	if err := engine.UpdatePolicy(*policy, *pool); err != nil {
		logger.Fatalf("invalid initial policy configuration: %v", err)
	}

	ctx, stop := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
	defer stop()

	var zmqSubscriber *zmqsub.Subscriber
	if strings.TrimSpace(*zmqEndpoints) != "" {
		eps := strings.Split(*zmqEndpoints, ",")
		zmqSubscriber = zmqsub.NewSubscriber(zmqsub.SubscriberConfig{
			Endpoints:    eps,
			TopicPrefix:  *zmqTopic,
			AllowedRoles: parseAllowedRoles(*zmqRoleSelector),
			Logger:       logger,
		}, index)
		zmqSubscriber.Start(ctx)
	}

	eppServer := extproc.NewServer(engine, index, telemetry, *blockSize, hashSeed, logger)

	grpcLis, err := net.Listen("tcp", fmt.Sprintf(":%d", *grpcPort))
	if err != nil {
		logger.Fatalf("failed to bind gRPC port %d: %v", *grpcPort, err)
	}

	grpcServer := grpc.NewServer(
		grpc.MaxRecvMsgSize(32*1024*1024),
		grpc.MaxSendMsgSize(32*1024*1024),
	)
	extprocv3.RegisterExternalProcessorServer(grpcServer, eppServer)
	healthSrv := health.NewServer()
	healthSrv.SetServingStatus("", healthpb.HealthCheckResponse_SERVING)
	healthSrv.SetServingStatus("envoy.service.ext_proc.v3.ExternalProcessor", healthpb.HealthCheckResponse_SERVING)
	healthpb.RegisterHealthServer(grpcServer, healthSrv)

	adminServer := &http.Server{
		Addr:              fmt.Sprintf(":%d", *metricsPort),
		Handler:           eppServer.NewAdminMux(),
		ReadHeaderTimeout: 5 * time.Second,
	}

	go func() {
		logger.Printf("starting Admin & Prometheus HTTP server on :%d", *metricsPort)
		if err := adminServer.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
			logger.Fatalf("admin HTTP server error: %v", err)
		}
	}()

	go func() {
		logger.Printf(
			"starting Envoy ext_proc gRPC server on :%d (policy=%s pool=%s blockSize=%d hashSeed=%d)",
			*grpcPort, *policy, *pool, *blockSize, hashSeed,
		)
		if err := grpcServer.Serve(grpcLis); err != nil {
			logger.Fatalf("gRPC server error: %v", err)
		}
	}()

	<-ctx.Done()
	logger.Printf("shutting down gracefully...")

	shutdownCtx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	_ = adminServer.Shutdown(shutdownCtx)
	grpcServer.GracefulStop()
	if zmqSubscriber != nil {
		zmqSubscriber.Wait()
	}
}
