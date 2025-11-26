#!/usr/bin/env bash
set -euo pipefail

curl -s http://localhost:8000/health | jq .

curl -s -X POST http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"channel":"web","user_id":"u1","message":"Tengeneza mpango wa somo wa hesabu kwa darasa la 4","domain":"education"}' | jq .
