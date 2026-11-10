// Copyright 2026 Rabimba Karanjai & Contributors.
// Licensed under the Apache License, Version 2.0.

package zmqsub_test

import (
	"context"
	"fmt"
	"net"
	"os/exec"
	"testing"
	"time"

	"github.com/rkaranjai/kubecon26-fleetkv-gke/router/pkg/radix"
	"github.com/rkaranjai/kubecon26-fleetkv-gke/router/pkg/zmqsub"
)

func getFreePort(t *testing.T) int {
	t.Helper()
	l, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		t.Fatalf("listen free port: %v", err)
	}
	defer func() { _ = l.Close() }()
	return l.Addr().(*net.TCPAddr).Port
}

func TestPyZMQPubToGoZMQSubJSONAndMsgPack(t *testing.T) {
	port := getFreePort(t)
	endpoint := fmt.Sprintf("tcp://127.0.0.1:%d", port)

	idx := radix.NewClusterIndex(nil)
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	sub := zmqsub.NewSubscriber(zmqsub.SubscriberConfig{
		Endpoints: []string{endpoint},
	}, idx)
	sub.Start(ctx)
	defer sub.Wait()

	// Launch a real Python pyzmq PUB process emitting both JSON and MsgPack KV events.
	pyCode := fmt.Sprintf(`
import json, time, msgpack, zmq
ctx = zmq.Context()
pub = ctx.socket(zmq.PUB)
pub.setsockopt(zmq.LINGER, 0)
pub.bind("tcp://127.0.0.1:%d")
time.sleep(0.25)

ev_store = {
    "event_type": "BlockStored",
    "pod_id": "prefill-0",
    "ip_port": "127.0.0.1:8003",
    "role": "prefill",
    "block_hashes": ["00000000000000a1", "00000000000000a2", "00000000000000a3"],
    "free_hbm_blocks": 357,
    "hbm_capacity_blocks": 360,
    "tier": "hbm",
}
pub.send(json.dumps(ev_store).encode("utf-8"))
time.sleep(0.05)

ev_remove = {
    "event_type": "BlockRemoved",
    "pod_id": "prefill-0",
    "ip_port": "127.0.0.1:8003",
    "role": "prefill",
    "block_hashes": ["00000000000000a3"],
    "free_hbm_blocks": 358,
    "tier": "hbm",
}
pub.send(msgpack.packb(ev_remove, use_bin_type=True))
time.sleep(0.1)
pub.close()
ctx.term()
`, port)

	cmd := exec.Command("python3", "-c", pyCode)
	if out, err := cmd.CombinedOutput(); err != nil {
		t.Fatalf("pyzmq publisher failed: %v (output=%s)", err, string(out))
	}

	deadline := time.Now().Add(3 * time.Second)
	for time.Now().Before(deadline) {
		matches := idx.MatchPods([]string{"00000000000000a1", "00000000000000a2", "00000000000000a3"}, "prefill")
		if len(matches) == 1 && matches[0].MatchedHBMBlocks == 2 && matches[0].Pod.FreeHBMBlocks == 358 {
			cancel()
			return
		}
		time.Sleep(25 * time.Millisecond)
	}
	t.Fatalf("timed out waiting for ZMQ index convergence; pods=%+v", idx.SnapshotPods())
}
