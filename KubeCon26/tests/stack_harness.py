# Copyright 2026 Rabimba Karanjai & Contributors.
# Licensed under the Apache License, Version 2.0.
"""Reusable Subprocess + Real Envoy v1.31 E2E Test Harness."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
import os
from pathlib import Path
import random
import socket
import subprocess
import sys
import tempfile
import time
from typing import Iterator
import uuid

import httpx

REPO_ROOT = Path(__file__).resolve().parent.parent
EPP_BIN = REPO_ROOT / "router" / "bin" / "fleetkv-epp"
TWIN_SCRIPT = REPO_ROOT / "twin" / "tpu_worker_twin.py"


def allocate_safe_ports(count: int) -> list[int]:
    """Allocates unique free TCP ports in 18000..29999 outside Linux's 32768..60999 ephemeral range."""
    reserved_socks: list[socket.socket] = []
    ports: list[int] = []
    candidates = list(range(18000, 29900))
    random.shuffle(candidates)
    try:
        for port in candidates:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind(("127.0.0.1", port))
            except OSError:
                s.close()
                continue
            reserved_socks.append(s)
            ports.append(port)
            if len(ports) == count:
                return ports
        raise RuntimeError(f"Could not allocate {count} safe ports")
    finally:
        for s in reserved_socks:
            s.close()


def ensure_epp_binary() -> Path:
    if not EPP_BIN.exists():
        EPP_BIN.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["go", "build", "-o", str(EPP_BIN), "./cmd/fleetkv-epp"],
            cwd=str(REPO_ROOT / "router"),
            check=True,
        )
    return EPP_BIN


@dataclass
class LiveTwinStack:
    gateway_url: str
    epp_admin_url: str
    agg_urls: list[str]
    disagg_urls: list[str]

    @property
    def all_worker_metrics_urls(self) -> list[str]:
        return [f"{u}/metrics" for u in (self.agg_urls + self.disagg_urls)]

    @property
    def agg_metrics_urls(self) -> list[str]:
        return [f"{u}/metrics" for u in self.agg_urls]

    @property
    def disagg_metrics_urls(self) -> list[str]:
        return [f"{u}/metrics" for u in self.disagg_urls]

    def set_policy(self, policy: str, pool: str) -> None:
        r = httpx.post(
            f"{self.epp_admin_url}/admin/policy",
            json={"policy": policy, "pool": pool},
            timeout=5.0,
        )
        r.raise_for_status()

    def reset_all(self) -> None:
        for u in self.agg_urls + self.disagg_urls:
            httpx.post(f"{u}/admin/reset", timeout=5.0).raise_for_status()
        httpx.post(f"{self.epp_admin_url}/admin/reset", timeout=5.0).raise_for_status()


def _wait_http_ok(url: str, timeout_sec: float = 15.0) -> None:
    deadline = time.monotonic() + timeout_sec
    last_err: Exception | None = None
    while time.monotonic() < deadline:
        try:
            r = httpx.get(url, timeout=1.0)
            if r.status_code == 200:
                return
        except Exception as exc:
            last_err = exc
        time.sleep(0.08)
    raise TimeoutError(f"Service did not become healthy at {url}: {last_err}")


@contextmanager
def running_envoy_twin_stack(
    hbm_capacity_blocks: int = 360,
    num_agg_pods: int = 4,
) -> Iterator[LiveTwinStack]:
    """Boots aggregated + disaggregated Python TPU twin workers + Go fleetkv-epp + real Envoy v1.31."""
    epp_bin = ensure_epp_binary()
    procs: list[subprocess.Popen[bytes]] = []
    envoy_container_name = f"fleetkv-test-envoy-{uuid.uuid4().hex[:8]}"

    total_workers = num_agg_pods + 4  # agg-0..agg-(N-1) + prefill-0 + prefill-1 + decode-0 + decode-1
    ports = allocate_safe_ports(total_workers * 2 + 4)
    p_iter = iter(ports)

    worker_specs: list[tuple[str, str, int, int, bool]] = []
    for i in range(num_agg_pods):
        worker_specs.append((f"agg-{i}", "agg", next(p_iter), next(p_iter), False))
    worker_specs.append(("prefill-0", "prefill", next(p_iter), next(p_iter), True))
    worker_specs.append(("prefill-1", "prefill", next(p_iter), next(p_iter), True))
    worker_specs.append(("decode-0", "decode", next(p_iter), next(p_iter), False))
    worker_specs.append(("decode-1", "decode", next(p_iter), next(p_iter), False))

    epp_grpc, epp_metrics = next(p_iter), next(p_iter)
    envoy_http, envoy_admin = next(p_iter), next(p_iter)

    env = os.environ.copy()
    env["PYTHONHASHSEED"] = "0"

    with tempfile.TemporaryDirectory(prefix="fleetkv_e2e_") as tmpdir:
        try:
            for pod_id, role, h_port, z_port, hma_dram in worker_specs:
                cmd = [
                    sys.executable,
                    str(TWIN_SCRIPT),
                    f"--pod-id={pod_id}",
                    f"--role={role}",
                    "--host=127.0.0.1",
                    f"--port={h_port}",
                    f"--zmq-pub-port={z_port}",
                    f"--advertise-addr=127.0.0.1:{h_port}",
                    "--block-size=256",
                    f"--hbm-capacity-blocks={hbm_capacity_blocks}",
                ]
                if hma_dram:
                    cmd.extend(["--enable-hma-dram", "--dram-capacity-blocks=4096"])
                procs.append(
                    subprocess.Popen(
                        cmd,
                        env=env,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.PIPE,
                    )
                )

            for _, _, h_port, _, _ in worker_specs:
                _wait_http_ok(f"http://127.0.0.1:{h_port}/healthz")

            zmq_eps = ",".join(f"tcp://127.0.0.1:{z}" for _, _, _, z, _ in worker_specs)
            static_pods = ",".join(
                f"{pid}=127.0.0.1:{hp}:{role}:{hbm_capacity_blocks}"
                for pid, role, hp, _, _ in worker_specs
            )

            epp_cmd = [
                str(epp_bin),
                f"--grpc-port={epp_grpc}",
                f"--metrics-port={epp_metrics}",
                "--policy=round_robin",
                "--pool=agg",
                "--block-size=256",
                "--safety-reserve-blocks=24",
                "--peak-prefill-tokens=12288",
                f"--zmq-endpoints={zmq_eps}",
                f"--static-pods={static_pods}",
            ]
            procs.append(
                subprocess.Popen(
                    epp_cmd,
                    env=env,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                )
            )
            _wait_http_ok(f"http://127.0.0.1:{epp_metrics}/healthz")

            agg_lb_yaml = "\n".join(
                f"              - endpoint:\n                  address:\n                    socket_address: {{ address: 127.0.0.1, port_value: {hp} }}"
                for _, role, hp, _, _ in worker_specs
                if role == "agg"
            )

            envoy_cfg = f"""
admin:
  address:
    socket_address: {{ address: 127.0.0.1, port_value: {envoy_admin} }}
static_resources:
  listeners:
    - name: ingress
      address:
        socket_address: {{ address: 127.0.0.1, port_value: {envoy_http} }}
      filter_chains:
        - filters:
            - name: envoy.filters.network.http_connection_manager
              typed_config:
                "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
                stat_prefix: ingress_http
                stream_idle_timeout: 300s
                route_config:
                  name: local_route
                  virtual_hosts:
                    - name: backend
                      domains: ["*"]
                      routes:
                        - match:
                            prefix: "/"
                            headers:
                              - name: x-gateway-destination-endpoint
                                present_match: true
                          route: {{ cluster: gaie_endpoint_picker_cluster, timeout: 0s }}
                        - match: {{ prefix: "/" }}
                          route: {{ cluster: stage1_agg_round_robin, timeout: 0s }}
                http_filters:
                  - name: envoy.filters.http.ext_proc
                    typed_config:
                      "@type": type.googleapis.com/envoy.extensions.filters.http.ext_proc.v3.ExternalProcessor
                      grpc_service:
                        envoy_grpc: {{ cluster_name: fleetkv_epp_grpc }}
                        timeout: 15s
                      failure_mode_allow: false
                      message_timeout: 10s
                      processing_mode:
                        request_header_mode: SEND
                        response_header_mode: SEND
                        request_body_mode: BUFFERED
                        response_body_mode: NONE
                        request_trailer_mode: SKIP
                        response_trailer_mode: SKIP
                  - name: envoy.filters.http.router
                    typed_config:
                      "@type": type.googleapis.com/envoy.extensions.filters.http.router.v3.Router
  clusters:
    - name: fleetkv_epp_grpc
      connect_timeout: 3s
      type: STATIC
      lb_policy: ROUND_ROBIN
      typed_extension_protocol_options:
        envoy.extensions.upstreams.http.v3.HttpProtocolOptions:
          "@type": type.googleapis.com/envoy.extensions.upstreams.http.v3.HttpProtocolOptions
          explicit_http_config:
            http2_protocol_options: {{}}
      load_assignment:
        cluster_name: fleetkv_epp_grpc
        endpoints:
          - lb_endpoints:
              - endpoint:
                  address:
                    socket_address: {{ address: 127.0.0.1, port_value: {epp_grpc} }}
    - name: gaie_endpoint_picker_cluster
      connect_timeout: 5s
      type: ORIGINAL_DST
      lb_policy: CLUSTER_PROVIDED
      original_dst_lb_config:
        use_http_header: true
        http_header_name: x-gateway-destination-endpoint
    - name: stage1_agg_round_robin
      connect_timeout: 5s
      type: STATIC
      lb_policy: ROUND_ROBIN
      load_assignment:
        cluster_name: stage1_agg_round_robin
        endpoints:
          - lb_endpoints:
{agg_lb_yaml}
"""
            cfg_path = Path(tmpdir) / "envoy.yaml"
            cfg_path.write_text(envoy_cfg, encoding="utf-8")
            os.chmod(tmpdir, 0o755)
            os.chmod(cfg_path, 0o644)

            procs.append(
                subprocess.Popen(
                    [
                        "docker",
                        "run",
                        "--rm",
                        "--name",
                        envoy_container_name,
                        "--network",
                        "host",
                        "-v",
                        f"{cfg_path}:/etc/envoy/envoy.yaml:ro",
                        "envoyproxy/envoy:v1.31-latest",
                        "-c",
                        "/etc/envoy/envoy.yaml",
                        "--log-level",
                        "warn",
                    ],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                )
            )
            _wait_http_ok(f"http://127.0.0.1:{envoy_admin}/ready")
            time.sleep(0.25)

            agg_urls = [
                f"http://127.0.0.1:{hp}" for _, role, hp, _, _ in worker_specs if role == "agg"
            ]
            disagg_urls = [
                f"http://127.0.0.1:{hp}" for _, role, hp, _, _ in worker_specs if role != "agg"
            ]
            yield LiveTwinStack(
                gateway_url=f"http://127.0.0.1:{envoy_http}",
                epp_admin_url=f"http://127.0.0.1:{epp_metrics}",
                agg_urls=agg_urls,
                disagg_urls=disagg_urls,
            )
        finally:
            subprocess.run(
                ["docker", "rm", "-f", envoy_container_name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
            for p in reversed(procs):
                p.terminate()
            for p in reversed(procs):
                try:
                    p.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    p.kill()
