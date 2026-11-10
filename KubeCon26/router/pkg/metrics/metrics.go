// Copyright 2026 Rabimba Karanjai & Contributors.
// Licensed under the Apache License, Version 2.0.

package metrics

import (
	"net/http"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

// Telemetry holds all FleetKV Endpoint Picker Prometheus metrics.
type Telemetry struct {
	Registry            *prometheus.Registry
	RadixBlocksTotal    prometheus.Gauge
	RouteDecisionsTotal *prometheus.CounterVec
	HerdSpilloversTotal prometheus.Counter
	ZMQEventsTotal      *prometheus.CounterVec
	PodFreeHBMBlocks    *prometheus.GaugeVec
	PodEvictionsTotal   *prometheus.CounterVec
}

// NewTelemetry creates an isolated Prometheus registry and registers FleetKV metrics.
func NewTelemetry() *Telemetry {
	reg := prometheus.NewRegistry()
	t := &Telemetry{
		Registry: reg,
		RadixBlocksTotal: prometheus.NewGauge(prometheus.GaugeOpts{
			Name: "fleetkv_radix_blocks_total",
			Help: "Total unique 256-token prefix blocks currently indexed in the cluster radix tree.",
		}),
		RouteDecisionsTotal: prometheus.NewCounterVec(prometheus.CounterOpts{
			Name: "fleetkv_route_decisions_total",
			Help: "Total routing decisions emitted by FleetKV ext_proc router.",
		}, []string{"policy", "target", "reason"}),
		HerdSpilloversTotal: prometheus.NewCounter(prometheus.CounterOpts{
			Name: "fleetkv_herd_spillovers_total",
			Help: "Total number of requests spilled over from a hot prefix pod due to HBM Fit Gate or queue threshold.",
		}),
		ZMQEventsTotal: prometheus.NewCounterVec(prometheus.CounterOpts{
			Name: "fleetkv_zmq_events_total",
			Help: "Total ZeroMQ KV cache block events ingested from serving pods.",
		}, []string{"event_type", "pod_id", "tier"}),
		PodFreeHBMBlocks: prometheus.NewGaugeVec(prometheus.GaugeOpts{
			Name: "fleetkv_pod_free_hbm_blocks",
			Help: "Reported free HBM 256-token blocks per serving pod.",
		}, []string{"pod_id", "role"}),
		PodEvictionsTotal: prometheus.NewCounterVec(prometheus.CounterOpts{
			Name: "fleetkv_pod_evictions_total",
			Help: "Total HBM BlockRemoved eviction events observed per serving pod.",
		}, []string{"pod_id"}),
	}

	reg.MustRegister(
		t.RadixBlocksTotal,
		t.RouteDecisionsTotal,
		t.HerdSpilloversTotal,
		t.ZMQEventsTotal,
		t.PodFreeHBMBlocks,
		t.PodEvictionsTotal,
	)
	return t
}

// Handler returns an http.Handler serving Prometheus exposition format.
func (t *Telemetry) Handler() http.Handler {
	return promhttp.HandlerFor(t.Registry, promhttp.HandlerOpts{})
}
