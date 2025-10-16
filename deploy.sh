#!/bin/bash

# First export all env variables from agents' .env files

# Name it accordingly to your agents
AGENTS=("rag" "llm_auditor" "marketing_agency" "travel_concierge" "short_movie")

ENV_VARS=""

for agent in "${AGENTS[@]}"; do
  # Load .env file and convert to comma-separated format
  AGENT_ENV=$(grep -v '^#' "${agent}/${agent}/.env" | grep -v '^$' | tr '\n' ',' | sed 's/,$//')
  
  # Append to ENV_VARS with comma separator if not empty
  if [ -n "$ENV_VARS" ]; then
    ENV_VARS="${ENV_VARS},${AGENT_ENV}"
  else
    ENV_VARS="${AGENT_ENV}"
  fi
  
  # Export variables to current shell
  export $(grep -v '^#' "${agent}/${agent}/.env" | grep -v '^$' | xargs)
done

echo "ENV vars:"
echo $ENV_VARS

SERVICE_NAME=adk-demo-mikolaj

gcloud run deploy $SERVICE_NAME \
    --source gcloud_deploy/ \
    --region "$GOOGLE_CLOUD_LOCATION" \
    --project "$GOOGLE_CLOUD_PROJECT" \
    --set-env-vars="$ENV_VARS"

gcloud run services update $SERVICE_NAME \
    --service-account=$SERVICE_ACCOUNT \
    --region=$GOOGLE_CLOUD_LOCATION