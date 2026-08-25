#!/usr/bin/env bash
set -e

# GCP Cloud Run Automated Deployment Script
PROJECT_ID=${GCP_PROJECT_ID:-"university-research-ai"}
REGION=${GCP_LOCATION:-"us-central1"}
SERVICE_NAME="research-knowledge-graph"
IMAGE_TAG="gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest"

echo "=========================================================="
echo " Deploying ${SERVICE_NAME} to Google Cloud Run"
echo " Project: ${PROJECT_ID} | Region: ${REGION}"
echo "=========================================================="

# 1. Build Container with Cloud Build
echo "[1/3] Submitting Cloud Build..."
gcloud builds submit --tag ${IMAGE_TAG} --project ${PROJECT_ID} ..

# 2. Deploy to Cloud Run
echo "[2/3] Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_TAG} \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --min-instances 1 \
    --max-instances 10 \
    --set-env-vars="GCP_PROJECT_ID=${PROJECT_ID},GCP_LOCATION=${REGION}" \
    --project ${PROJECT_ID}

echo "[3/3] Deployment completed successfully!"
gcloud run services describe ${SERVICE_NAME} --platform managed --region ${REGION} --format="value(status.url)"
