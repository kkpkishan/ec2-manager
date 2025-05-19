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
  -e USERNAME=admin \
  -e PASSWORD_HASH=scrypt:32768:8:1$AedvgQJbYOaipHfA$0d1dbfd6296416d1b7ec079b882cf760946ed4fe31652b6bb2a30976b9cc2f3f9187a8c3f328202dc7bb769c5a41ddc5b40b545c1d533b66daa0184b435658d1 \
  -e AWS_REGION=ap-south-1 \
  -e FLASK_SECRET_KEY=change_me_to_a_random_string \
  -e FLASK_DEBUG=1 \
  -e PORT=5000 \
  --full-entrypoint "python app.py"
