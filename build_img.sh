#! /usr/bin/bash

# Build the frontend artifact.
cd frontend
pnpm run build

# Build the backend artifact.
#cd ../backend
#uv build

# Build the Docker image.
DOCKERFILE_PATH="Dockerfile-cuda"
IMG_NAME="speak"
IMG_TAG="cuda-12.8.1"
cd ..
docker build -f ${DOCKERFILE_PATH} -t ${IMG_NAME}:${IMG_TAG} .
