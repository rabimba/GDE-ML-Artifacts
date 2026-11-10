// Copyright 2026 Rabimba Karanjai & Contributors.
// Licensed under the Apache License, Version 2.0.

package zmqsub

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"log"
	"strings"
	"sync"
	"time"

	"github.com/go-zeromq/zmq4"
	"github.com/vmihailenco/msgpack/v5"

	"github.com/rkaranjai/kubecon26-fleetkv-gke/router/pkg/radix"
)

// SubscriberConfig configures real ZeroMQ SUB ingestion from serving pods.
type SubscriberConfig struct {
	Endpoints    []string
	TopicPrefix  string
	AllowedRoles map[string]bool
	Logger       *log.Logger
}

// Subscriber manages concurrent ZeroMQ SUB loops feeding a ClusterIndex.
type Subscriber struct {
	cfg   SubscriberConfig
	index *radix.ClusterIndex
	wg    sync.WaitGroup
}

// NewSubscriber constructs a ZeroMQ KV event subscriber bound to index.
func NewSubscriber(cfg SubscriberConfig, index *radix.ClusterIndex) *Subscriber {
	return &Subscriber{
		cfg:   cfg,
		index: index,
	}
}

// Start launches background ZMQ SUB readers for all configured TCP endpoints.
func (s *Subscriber) Start(ctx context.Context) {
	for _, rawEP := range s.cfg.Endpoints {
		ep := strings.TrimSpace(rawEP)
		if ep == "" {
			continue
		}
		if !strings.Contains(ep, "://") {
			ep = "tcp://" + ep
		}
		s.wg.Add(1)
		go func(endpoint string) {
			defer s.wg.Done()
			s.consumeEndpointLoop(ctx, endpoint)
		}(ep)
	}
}

// Wait blocks until all ZMQ subscriber goroutines have exited after ctx cancellation.
func (s *Subscriber) Wait() {
	s.wg.Wait()
}

func (s *Subscriber) consumeEndpointLoop(ctx context.Context, endpoint string) {
	backoff := 100 * time.Millisecond
	for {
		if ctx.Err() != nil {
			return
		}
		err := s.runSingleSession(ctx, endpoint)
		if ctx.Err() != nil {
			return
		}
		if s.cfg.Logger != nil && err != nil {
			s.cfg.Logger.Printf("[zmqsub] endpoint=%s session ended (%v); reconnecting in %v", endpoint, err, backoff)
		}
		select {
		case <-ctx.Done():
			return
		case <-time.After(backoff):
		}
		if backoff < time.Second {
			backoff *= 2
		}
	}
}

func (s *Subscriber) runSingleSession(ctx context.Context, endpoint string) error {
	sub := zmq4.NewSub(ctx, zmq4.WithAutomaticReconnect(true))
	defer func() { _ = sub.Close() }()

	if err := sub.Dial(endpoint); err != nil {
		return fmt.Errorf("dial %s: %w", endpoint, err)
	}
	if err := sub.SetOption(zmq4.OptionSubscribe, s.cfg.TopicPrefix); err != nil {
		return fmt.Errorf("subscribe %s: %w", endpoint, err)
	}
	if s.cfg.Logger != nil {
		s.cfg.Logger.Printf("[zmqsub] connected ZeroMQ SUB -> %s (topic=%q)", endpoint, s.cfg.TopicPrefix)
	}

	for {
		msg, err := sub.Recv()
		if err != nil {
			return err
		}
		events, err := DecodeKVEventFrames(msg.Frames)
		if err != nil {
			if s.cfg.Logger != nil {
				s.cfg.Logger.Printf("[zmqsub] decode error from %s: %v", endpoint, err)
			}
			continue
		}
		for _, ev := range events {
			if len(s.cfg.AllowedRoles) > 0 && ev.Role != "" {
				if !s.cfg.AllowedRoles[strings.ToLower(ev.Role)] {
					continue
				}
			}
			_ = s.index.ApplyEvent(ev)
		}
	}
}

// DecodeKVEventFrames parses single-frame [payload] or multipart [topic, payload] frames
// encoded in either JSON or MessagePack (single event object or batch array).
func DecodeKVEventFrames(frames [][]byte) ([]radix.KVEvent, error) {
	if len(frames) == 0 {
		return nil, fmt.Errorf("empty zmq message frames")
	}
	payload := frames[len(frames)-1]
	trimmed := bytes.TrimSpace(payload)
	if len(trimmed) == 0 {
		return nil, fmt.Errorf("empty zmq payload")
	}

	// JSON object or JSON array
	if trimmed[0] == '{' {
		var single radix.KVEvent
		if err := json.Unmarshal(trimmed, &single); err != nil {
			return nil, fmt.Errorf("json decode object: %w", err)
		}
		return []radix.KVEvent{single}, nil
	}
	if trimmed[0] == '[' {
		var batch []radix.KVEvent
		if err := json.Unmarshal(trimmed, &batch); err != nil {
			return nil, fmt.Errorf("json decode array: %w", err)
		}
		return batch, nil
	}

	// MessagePack single map or array
	var single radix.KVEvent
	if err := msgpack.Unmarshal(payload, &single); err == nil && single.EventType != "" {
		return []radix.KVEvent{single}, nil
	}
	var batch []radix.KVEvent
	if err := msgpack.Unmarshal(payload, &batch); err == nil && len(batch) > 0 {
		return batch, nil
	}
	return nil, fmt.Errorf("unrecognized zmq payload encoding (%d bytes)", len(payload))
}
