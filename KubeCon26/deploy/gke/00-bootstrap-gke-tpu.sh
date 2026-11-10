#!/usr/bin/env bash
# Copyright 2026 Rabimba Karanjai & Contributors.
# Licensed under the Apache License, Version 2.0.
#
# Production GKE Cloud TPU v6e (Trillium) Cluster & GAIE v1 Bootstrap Script.
# Configures a custom MTU=8896 jumbo-frame gVNIC VPC, proxy-only RILB subnet,
# GKE Rapid cluster, 2x ct6e-standard-4t (8 TPU v6e chips) node pools,
# Gateway API Inference Extension v1 CRDs, LeaderWorkerSet v0.11.1, and llm-d.

set -euo pipefail

PROJECT_ID="${PROJECT_ID:-$(gcloud config get-value project)}"
REGION="${REGION:-us-east5}"
ZONE="${ZONE:-us-east5-a}"
CLUSTER_NAME="${CLUSTER_NAME:-fleetkv-tpu-kcon26}"
VPC_NAME="${VPC_NAME:-fleetkv-tpu-vpc}"
SUBNET_NAME="${SUBNET_NAME:-fleetkv-tpu-subnet}"
PROXY_SUBNET_NAME="${PROXY_SUBNET_NAME:-fleetkv-rilb-proxy-subnet}"

echo "==> [1/6] Creating Jumbo-Frame gVNIC VPC (${VPC_NAME}, MTU=8896)"
gcloud compute networks create "${VPC_NAME}" \
  --project="${PROJECT_ID}" \
  --subnet-mode=custom \
  --mtu=8896 \
  --bgp-routing-mode=regional

gcloud compute networks subnets create "${SUBNET_NAME}" \
  --project="${PROJECT_ID}" \
  --network="${VPC_NAME}" \
  --region="${REGION}" \
  --range="10.40.0.0/20" \
  --secondary-range="pods=10.48.0.0/14,services=10.52.0.0/20"

echo "==> [2/6] Creating Regional Managed Proxy-Only Subnet for gke-l7-rilb Gateway"
gcloud compute networks subnets create "${PROXY_SUBNET_NAME}" \
  --project="${PROJECT_ID}" \
  --network="${VPC_NAME}" \
  --region="${REGION}" \
  --purpose=REGIONAL_MANAGED_PROXY \
  --role=ACTIVE \
  --range="10.53.0.0/23"

echo "==> [3/6] Creating GKE Rapid Cluster (${CLUSTER_NAME}) with Dataplane V2 & Gateway API"
gcloud container clusters create "${CLUSTER_NAME}" \
  --project="${PROJECT_ID}" \
  --zone="${ZONE}" \
  --release-channel=rapid \
  --network="${VPC_NAME}" \
  --subnetwork="${SUBNET_NAME}" \
  --cluster-secondary-range-name=pods \
  --services-secondary-range-name=services \
  --enable-ip-alias \
  --enable-dataplane-v2 \
  --enable-gvnic \
  --gateway-api=standard \
  --addons=HttpLoadBalancing,GcePersistentDiskCsiDriver \
  --machine-type=e2-standard-8 \
  --num-nodes=2 \
  --workload-pool="${PROJECT_ID}.svc.id.goog"

gcloud container clusters get-credentials "${CLUSTER_NAME}" \
  --project="${PROJECT_ID}" \
  --zone="${ZONE}"

echo "==> [4/6] Provisioning Trillium TPU v6e Node Pools (ct6e-standard-4t, 2x2 topology)"
# Pool A: 2x ct6e-standard-4t (8 TPU v6e chips) for Baseline Aggregated Serving
gcloud container node-pools create tpu-v6e-agg-pool \
  --project="${PROJECT_ID}" \
  --cluster="${CLUSTER_NAME}" \
  --zone="${ZONE}" \
  --machine-type=ct6e-standard-4t \
  --tpu-topology=2x2 \
  --num-nodes=2 \
  --enable-gvnic \
  --node-labels="fleetkv.io/pool=agg"

# Pool B: 2x ct6e-standard-4t (8 TPU v6e chips: 1x 4-chip Prefill + 1x 4-chip Decode)
gcloud container node-pools create tpu-v6e-disagg-pool \
  --project="${PROJECT_ID}" \
  --cluster="${CLUSTER_NAME}" \
  --zone="${ZONE}" \
  --machine-type=ct6e-standard-4t \
  --tpu-topology=2x2 \
  --num-nodes=2 \
  --enable-gvnic \
  --node-labels="fleetkv.io/pool=disagg"

echo "==> [5/6] Installing Gateway API Inference Extension (GAIE v1.0.0) & LeaderWorkerSet v0.11.1"
kubectl apply -f https://github.com/kubernetes-sigs/gateway-api-inference-extension/releases/download/v1.0.0/manifests.yaml
kubectl apply --server-side -f https://github.com/kubernetes-sigs/lws/releases/download/v0.11.1/manifests.yaml

echo "==> [6/6] Installing llm-d DisaggregatedSet Controller"
kubectl apply -f https://github.com/llm-d/llm-d-deployer/releases/download/v0.3.0/disaggregatedset-operator.yaml

kubectl create namespace fleetkv-serving --dry-run=client -o yaml | kubectl apply -f -
echo "Bootstrap complete. Apply 01, 02, and 03 manifests into namespace fleetkv-serving."
