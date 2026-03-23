#!/bin/bash
# Simple script to run the local Docker container

echo "==========================================="
echo "  Starting CORA Datalens Local Container"
echo "==========================================="

docker run --rm -p 8085:8080 \
  --env-file .env \
  -v "$(pwd)/database:/app/database" \
  -v "$(pwd)/Backend/catelogue:/app/Backend/catelogue" \
  cora-datalens-local
