#!/bin/bash

CONTAINER_NAME="ec2-dashboard"

# Stop and remove if already running
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
  echo "Stopping existing container: $CONTAINER_NAME"
  docker stop "$CONTAINER_NAME"
  docker rm "$CONTAINER_NAME"
fi

# Run container using iam-docker-run
echo "Starting container with iam-docker-run..."

iam-docker-run \
  --image ec2-dashboard:latest \
  --name "$CONTAINER_NAME" \
  -d \
  -p 80:5000 \
  -e USERNAME=vipul.shah@rubamin.com \
  -e PASSWORD_HASH=scrypt:32768:8:1$ZP8jMy3qFvbyrhaS$4c1ebc350f48a942f0492165f99aad6013a368f309d67058a8a99c55a195319fbf5c925bce395e62ac31daf7789884f1fe093c77d3c5b5cc2716dac4eb79cee9 \
  -e AWS_REGION=ap-south-1 \
  -e FLASK_SECRET_KEY=change_me_to_a_random_string \
  -e FLASK_DEBUG=1 \
  -e PORT=5000 \
  --full-entrypoint "python app.py"
