# Copyright 2026 Rabimba Karanjai & Contributors.
# Licensed under the Apache License, Version 2.0.
"""Gate G2: Production GKE Cloud TPU & GAIE Manifest Invariant Audit."""

from __future__ import annotations

from pathlib import Path
import subprocess
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
GKE_DIR = REPO_ROOT / "deploy" / "gke"


def _iter_containers(obj: Any) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    if isinstance(obj, dict):
        if "containers" in obj and isinstance(obj["containers"], list):
            for c in obj["containers"]:
                if isinstance(c, dict) and "image" in c:
                    found.append(c)
        for v in obj.values():
            found.extend(_iter_containers(v))
    elif isinstance(obj, list):
        for item in obj:
            found.extend(_iter_containers(item))
    return found


def _load_all_gke_yaml_docs() -> list[tuple[Path, dict[str, Any]]]:
    yaml_files = sorted(GKE_DIR.glob("*.yaml"))
    assert len(yaml_files) >= 3, f"Expected >= 3 YAML manifests in {GKE_DIR}, found {yaml_files}"
    docs: list[tuple[Path, dict[str, Any]]] = []
    for yf in yaml_files:
        raw = yf.read_text(encoding="utf-8")
        parsed = list(yaml.safe_load_all(raw))
        assert parsed, f"Empty YAML manifest: {yf}"
        for doc in parsed:
            if doc is not None:
                assert isinstance(doc, dict), f"Invalid K8s document in {yf}: {type(doc)}"
                assert "apiVersion" in doc and "kind" in doc, f"Missing apiVersion/kind in {yf}"
                docs.append((yf, doc))
    return docs


def test_bootstrap_script_syntax_and_mtu_8896_gvnic_invariants() -> None:
    script = GKE_DIR / "00-bootstrap-gke-tpu.sh"
    assert script.exists(), f"Missing {script}"
    subprocess.run(["bash", "-n", str(script)], check=True)

    content = script.read_text(encoding="utf-8")
    assert "--mtu=8896" in content, "VPC creation MUST configure --mtu=8896 jumbo frames for TPU Sync"
    assert "ct6e-standard-4t" in content, "GKE node pool MUST target Trillium ct6e-standard-4t TPUs"
    assert "REGIONAL_MANAGED_PROXY" in content, "Must provision proxy-only subnet for gke-l7-rilb Gateway"
    assert "gateway-api-inference-extension" in content, "Must install GAIE v1 CRDs"
    assert "lws/releases/download/v0.11.1" in content, "Must install LeaderWorkerSet v0.11.1"


def test_all_containers_pin_pythonhashseed_zero() -> None:
    docs = _load_all_gke_yaml_docs()
    containers: list[tuple[Path, dict[str, Any]]] = []
    for path, doc in docs:
        for c in _iter_containers(doc):
            containers.append((path, c))

    assert len(containers) >= 5, f"Expected >= 5 workload containers across manifests, got {len(containers)}"

    for path, c in containers:
        env_list = c.get("env") or []
        seed_vars = [e for e in env_list if isinstance(e, dict) and e.get("name") == "PYTHONHASHSEED"]
        assert len(seed_vars) == 1, (
            f"Container {c.get('name')} in {path.name} missing PYTHONHASHSEED env var"
        )
        val = seed_vars[0].get("value")
        assert val == "0" and isinstance(val, str), (
            f"Container {c.get('name')} in {path.name} must set PYTHONHASHSEED=\"0\" (str), got {val!r}"
        )


def test_block_size_256_parity_between_vllm_and_fleetkv_router() -> None:
    docs = _load_all_gke_yaml_docs()
    vllm_checked = 0
    epp_checked = 0

    for path, doc in docs:
        for c in _iter_containers(doc):
            image = str(c.get("image", ""))
            joined_args = " ".join(str(a) for a in (c.get("args") or []))
            if "vllm-torchtpu" in image:
                vllm_checked += 1
                assert "--block-size 256" in joined_args or "--block-size=256" in joined_args, (
                    f"vLLM container {c.get('name')} in {path.name} must pass --block-size 256; args={joined_args}"
                )
            if "fleetkv-epp" in image:
                epp_checked += 1
                assert "--block-size=256" in joined_args, (
                    f"EPP container {c.get('name')} in {path.name} must pass --block-size=256; args={joined_args}"
                )

    assert vllm_checked >= 3, f"Expected >= 3 vllm-torchtpu containers, checked {vllm_checked}"
    assert epp_checked >= 1, f"Expected >= 1 fleetkv-epp container, checked {epp_checked}"


def test_disaggregatedset_hma_dram_and_gaie_zmq_prefill_selector() -> None:
    docs = _load_all_gke_yaml_docs()

    found_disagg = False
    found_prefill_zmq_selector = False
    found_inference_pool_v1 = False
    found_httproute = False

    for path, doc in docs:
        kind = doc.get("kind")
        api_version = doc.get("apiVersion")

        if kind == "DisaggregatedSet":
            found_disagg = True
            raw_text = yaml.dump(doc)
            assert "TPUConnectorHMA" in raw_text, "DisaggregatedSet must configure TPUConnectorHMA"
            assert "64Gi" in raw_text, "DisaggregatedSet must mount 64Gi /dev/shm volume"
            assert "5557" in raw_text, "DisaggregatedSet prefill must publish ZMQ KV events on port 5557"

        if kind == "Deployment" and doc.get("metadata", {}).get("name") == "fleetkv-epp":
            for c in _iter_containers(doc):
                joined_args = " ".join(str(a) for a in (c.get("args") or []))
                if "llm-d.ai/role=prefill" in joined_args:
                    found_prefill_zmq_selector = True

        if kind == "InferencePool" and api_version == "inference.networking.k8s.io/v1":
            found_inference_pool_v1 = True

        if kind == "HTTPRoute" and api_version == "gateway.networking.k8s.io/v1":
            backends = doc["spec"]["rules"][0]["backendRefs"]
            assert len(backends) == 3, f"Expected 3-stage HTTPRoute backendRefs, got {len(backends)}"
            found_httproute = True

    assert found_disagg, "Missing DisaggregatedSet manifest"
    assert found_prefill_zmq_selector, "fleetkv-epp must filter ZMQ discovery to llm-d.ai/role=prefill"
    assert found_inference_pool_v1, "Missing inference.networking.k8s.io/v1 InferencePool"
    assert found_httproute, "Missing 3-way Gateway API HTTPRoute"


def test_headless_services_expose_zmq_and_http_ports_for_pod_discovery() -> None:
    docs = _load_all_gke_yaml_docs()
    headless_svcs: dict[str, set[int]] = {}
    for _, doc in docs:
        if doc.get("kind") == "Service" and doc.get("spec", {}).get("clusterIP") == "None":
            name = doc.get("metadata", {}).get("name", "")
            ports = {int(p["port"]) for p in doc.get("spec", {}).get("ports", []) if "port" in p}
            headless_svcs[name] = ports

    assert "vllm-agg-headless-svc" in headless_svcs, "Missing vllm-agg-headless-svc for per-pod ZMQ/HTTP discovery"
    assert {8000, 5557}.issubset(headless_svcs["vllm-agg-headless-svc"])
    assert "qwen3-prefill-headless-svc" in headless_svcs, "Missing qwen3-prefill-headless-svc"
    assert {8000, 5557}.issubset(headless_svcs["qwen3-prefill-headless-svc"])
    assert "qwen3-decode-headless-svc" in headless_svcs, "Missing qwen3-decode-headless-svc"
    assert 8000 in headless_svcs["qwen3-decode-headless-svc"]
