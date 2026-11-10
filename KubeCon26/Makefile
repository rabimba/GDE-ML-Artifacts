# Copyright 2026 Rabimba Karanjai & Contributors.
# Licensed under the Apache License, Version 2.0.

SHELL := /bin/bash
.DEFAULT_GOAL := help

GO ?= go
PYTEST ?= pytest
PYTHON ?= python3

.PHONY: help build test gate-g0 gate-g1 gate-g2 gate-g3 gate-g4 gate-all twin-up twin-down demo-tmux slides-build slides-serve slides-export clean

help: ## Show available targets
	@grep -E '^[a-zA-Z0-9_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

build: ## Compile Go FleetKV GAIE ext_proc router binary
	cd router && mkdir -p bin && $(GO) build -trimpath -o bin/fleetkv-epp ./cmd/fleetkv-epp

test: gate-g0 gate-g2 ## Run fast unit & manifest audit tests

gate-g0: build ## Gate G0: Go router unit tests with race detector + Python hash/ZMQ parity
	cd router && $(GO) test -v -race ./...

gate-g1: build ## Gate G1: End-to-end 3-stage Envoy + Digital Twin physics & SLO verification
	PYTHONHASHSEED=0 $(PYTEST) -v -s tests/test_g1_radix_and_herd.py tests/test_g2_e2e_envoy_twin.py

gate-g2: ## Gate G2: Production GKE Cloud TPU & GAIE YAML/Bash invariant audit
	$(PYTEST) -v tests/test_g3_k8s_manifests.py

gate-g3: twin-up ## Gate G3: Non-interactive Rich 4-column TUI 3-stage freeze smoke run
	PYTHONHASHSEED=0 $(PYTHON) bench/stage_tui.py --smoke-test --duration-sec 6

gate-g4: slides-build ## Gate G4: Slidev static deck build verification

gate-all: gate-g0 gate-g1 gate-g2 gate-g3 gate-g4 ## Execute all 5 deterministic verification gates (G0-G4)

twin-up: ## Build and start the local Envoy + FleetKV EPP + TPU Twin Docker Compose stack
	docker compose up -d --build
	@echo "==> Waiting for Envoy (:8080) and FleetKV EPP (:9090) readiness..."
	@for i in $$(seq 1 40); do \
		if curl -fsS http://127.0.0.1:9090/healthz >/dev/null 2>&1 && curl -fsS http://127.0.0.1:9901/ready >/dev/null 2>&1; then \
			echo "==> Local Digital Twin ready on http://127.0.0.1:8080"; \
			exit 0; \
		fi; \
		sleep 0.5; \
	done; \
	echo "ERROR: Local Digital Twin failed readiness check" >&2; exit 1

twin-down: ## Tear down the local Docker Compose Digital Twin stack
	docker compose down --remove-orphans

demo-tmux: twin-up ## Launch the 3-pane KubeCon live rehearsal tmux layout
	./bench/demo_ctl.sh prep --target=twin

slides-build: ## Install Slidev dependencies and build static HTML deck
	cd slides && npm install && npx slidev build

slides-serve: ## Launch interactive Slidev presentation & presenter view on http://localhost:3030
	cd slides && npx slidev --port 3030 --open

slides-export: ## Export presentation deck to PDF and PPTX in slides/
	cd slides && npx slidev export --output KubeCon26-FleetKV-GKE.pdf && npx slidev export --format pptx --output KubeCon26-FleetKV-GKE.pptx

clean: ## Remove build artifacts and caches
	rm -rf router/bin slides/dist .pytest_cache
