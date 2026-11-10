#!/usr/bin/env bash
# Copyright 2026 Rabimba Karanjai & Contributors.
# Licensed under the Apache License, Version 2.0.
#
# KubeCon 2026 One-Command Live Stage Controller.
# Supports both Local Digital Twin (--target=twin, default) and GKE Cloud TPU (--target=gke).
#
# Usage:
#   ./bench/demo_ctl.sh prep [--target=twin|gke]
#   ./bench/demo_ctl.sh stage1 [--target=twin|gke]
#   ./bench/demo_ctl.sh stage2 [--target=twin|gke]
#   ./bench/demo_ctl.sh stage3 [--target=twin|gke]
#   ./bench/demo_ctl.sh reset  [--target=twin|gke]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

TARGET="${FLEETKV_TARGET:-twin}"
GATEWAY_URL="${FLEETKV_GATEWAY_URL:-http://127.0.0.1:8080}"
EPP_ADMIN_URL="${FLEETKV_EPP_ADMIN_URL:-http://127.0.0.1:9090}"
K8S_NS="${FLEETKV_NAMESPACE:-fleetkv-serving}"
TMUX_SESSION="${FLEETKV_TMUX_SESSION:-fleetkv-kcon26}"

SUBCOMMAND=""
for arg in "$@"; do
  case "${arg}" in
    --target=*)
      TARGET="${arg#*=}"
      ;;
    --gateway-url=*)
      GATEWAY_URL="${arg#*=}"
      ;;
    --epp-admin-url=*)
      EPP_ADMIN_URL="${arg#*=}"
      ;;
    prep|stage1|stage1-round-robin|stage2|stage2-naive-kv|stage3|stage3-fleetkv-disagg|reset|status)
      SUBCOMMAND="${arg}"
      ;;
    *)
      echo "Unknown argument: ${arg}" >&2
      exit 1
      ;;
  esac
done

if [[ -z "${SUBCOMMAND}" ]]; then
  echo "Usage: $0 {prep|stage1|stage2|stage3|reset|status} [--target=twin|gke]" >&2
  exit 1
fi

patch_gke_httproute() {
  local w1="$1"
  local w2="$2"
  local w3="$3"
  kubectl patch httproute agent-fleet-route -n "${K8S_NS}" --type=merge -p "{
    \"spec\": {
      \"rules\": [{
        \"matches\": [{\"path\": {\"type\": \"PathPrefix\", \"value\": \"/v1\"}}],
        \"timeouts\": {\"request\": \"300s\", \"backendRequest\": \"300s\"},
        \"backendRefs\": [
          {\"group\": \"\", \"kind\": \"Service\", \"name\": \"vllm-agg-roundrobin-svc\", \"port\": 8000, \"weight\": ${w1}},
          {\"group\": \"inference.networking.k8s.io\", \"kind\": \"InferencePool\", \"name\": \"vllm-agg-naive-pool\", \"port\": 8000, \"weight\": ${w2}},
          {\"group\": \"inference.networking.k8s.io\", \"kind\": \"InferencePool\", \"name\": \"fleetkv-disagg-pool\", \"port\": 8000, \"weight\": ${w3}}
        ]
      }]
    }
  }"
}

switch_stage() {
  local stage="$1"
  case "${stage}" in
    stage1|stage1-round-robin)
      echo "==> Switching [${TARGET}] to STAGE 1: Stateless K8s Round-Robin (Aggregated Pool)"
      if [[ "${TARGET}" == "gke" ]]; then
        patch_gke_httproute 100 0 0
      else
        curl -fsS -X POST "${EPP_ADMIN_URL}/admin/policy" \
          -H "Content-Type: application/json" \
          -d '{"policy":"round_robin","pool":"agg"}'
        echo ""
      fi
      ;;

    stage2|stage2-naive-kv)
      echo "==> Switching [${TARGET}] to STAGE 2: Naive Longest-Prefix Sticky Routing (Watch Prefix-Herd!)"
      if [[ "${TARGET}" == "gke" ]]; then
        patch_gke_httproute 0 100 0
      else
        curl -fsS -X POST "${EPP_ADMIN_URL}/admin/policy" \
          -H "Content-Type: application/json" \
          -d '{"policy":"naive_sticky","pool":"agg"}'
        echo ""
      fi
      ;;

    stage3|stage3-fleetkv-disagg)
      echo "==> Switching [${TARGET}] to STAGE 3: FleetKV Fit-Aware + TorchTPU Disaggregated Serving"
      if [[ "${TARGET}" == "gke" ]]; then
        patch_gke_httproute 0 0 100
      else
        curl -fsS -X POST "${EPP_ADMIN_URL}/admin/policy" \
          -H "Content-Type: application/json" \
          -d '{"policy":"fleetkv_fit","pool":"disagg"}'
        echo ""
      fi
      ;;
  esac
}

case "${SUBCOMMAND}" in
  stage1|stage1-round-robin|stage2|stage2-naive-kv|stage3|stage3-fleetkv-disagg)
    switch_stage "${SUBCOMMAND}"
    ;;

  reset)
    echo "==> Resetting KV caches & returning [${TARGET}] to Stage 1..."
    if [[ "${TARGET}" == "twin" ]]; then
      for port in 8001 8002 8003 8004 8005 8006 8007 8008; do
        curl -fsS -X POST "http://127.0.0.1:${port}/admin/reset" >/dev/null || true
      done
      curl -fsS -X POST "${EPP_ADMIN_URL}/admin/reset" >/dev/null || true
    fi
    switch_stage stage1
    ;;

  status)
    if [[ "${TARGET}" == "gke" ]]; then
      kubectl get httproute,inferencepool,pods -n "${K8S_NS}"
    else
      curl -fsS "${EPP_ADMIN_URL}/admin/state" | python3 -m json.tool
    fi
    ;;

  prep)
    switch_stage stage1 || true

    if ! command -v tmux >/dev/null 2>&1; then
      echo "==> Note: 'tmux' not installed; launching 4-column Stage Scorecard TUI directly."
      echo "==> In another terminal tab, flip stages via:"
      echo "      ./bench/demo_ctl.sh stage2 --target=${TARGET}"
      echo "      ./bench/demo_ctl.sh stage3 --target=${TARGET}"
      FLEETKV_GATEWAY_URL="${GATEWAY_URL}" FLEETKV_EPP_ADMIN_URL="${EPP_ADMIN_URL}" \
        exec python3 "${REPO_ROOT}/bench/stage_tui.py"
    fi

    tmux kill-session -t "${TMUX_SESSION}" 2>/dev/null || true
    # Left 60% pane: Live 4-Column Rich Scorecard TUI
    tmux new-session -d -s "${TMUX_SESSION}" -c "${REPO_ROOT}" \
      "FLEETKV_GATEWAY_URL='${GATEWAY_URL}' FLEETKV_EPP_ADMIN_URL='${EPP_ADMIN_URL}' python3 bench/stage_tui.py"

    # Right 40% split -> Top-Right: Live EPP Radix Index & Route Decision Stream
    if [[ "${TARGET}" == "gke" ]]; then
      EPP_WATCH_CMD="kubectl logs -n '${K8S_NS}' -l app=fleetkv-epp -f --tail=25"
    else
      EPP_WATCH_CMD="FLEETKV_EPP_ADMIN_URL='${EPP_ADMIN_URL}' python3 bench/stage_tui.py --watch-epp"
    fi

    tmux split-window -h -l 40% -t "${TMUX_SESSION}:0.0" -c "${REPO_ROOT}" "${EPP_WATCH_CMD}" \
      || tmux split-window -h -p 40 -t "${TMUX_SESSION}:0.0" -c "${REPO_ROOT}" "${EPP_WATCH_CMD}"

    # Bottom-Right: Interactive Stage Operator Shell
    tmux split-window -v -l 45% -t "${TMUX_SESSION}:0.1" -c "${REPO_ROOT}" \
      || tmux split-window -v -p 45 -t "${TMUX_SESSION}:0.1" -c "${REPO_ROOT}"
    tmux send-keys -t "${TMUX_SESSION}:0.2" \
      "clear && echo '=== KubeCon 2026 Stage Operator ===' && echo 'Run:' && echo '  ./bench/demo_ctl.sh stage2 --target=${TARGET}' && echo '  ./bench/demo_ctl.sh stage3 --target=${TARGET}'" C-m

    tmux select-pane -t "${TMUX_SESSION}:0.2"
    if [[ -t 1 ]]; then
      exec tmux attach-session -t "${TMUX_SESSION}"
    else
      echo "Launched tmux session '${TMUX_SESSION}' in detached mode (attach via: tmux attach -t ${TMUX_SESSION})."
    fi
    ;;
esac
