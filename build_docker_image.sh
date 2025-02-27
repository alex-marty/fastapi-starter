#!/bin/bash

set -euxo pipefail

IMAGE_TAG="fastapi-starter"

uv lock
docker build -t ${IMAGE_TAG} .

# Instructions for deploying to Google Cloud Run

# To build for a Linux target, for example when building for Cloud Run on a Mac, add the
# option '--platform linux/amd64':
# docker build -t ${GCLOUD_API_IMAGE_TAG} --platform linux/x86_64 .

# To deploy to Cloud Run, push the image to a container registry and deploy the image:
# docker push ${GCLOUD_API_IMAGE_TAG}
# gcloud run deploy ${SERVICE_NAME} --image ${GCLOUD_API_IMAGE_TAG} --port ${SERVICE_PORT} \
#   --platform managed --region ${GCLOUD_REGION} --allow-unauthenticated
