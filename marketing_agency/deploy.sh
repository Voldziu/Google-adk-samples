#!/bin/bash


# Activate virtual environment
source .venv/bin/activate

# Load environment variables from .env file
if [ -f marketing_agency/.env ]; then
  export $(grep -v '^#' marketing_agency/.env | xargs)
fi

# Freeze requirements
uv pip freeze > requirements.txt

# Deploy to Cloud Run
# adk deploy agent_engine  $AGENT_PATH \
#   --display_name $SERVICE_NAME \
#   --staging_bucket $STAGING_BUCKET \
#   --region $GOOGLE_CLOUD_LOCATION \



adk deploy cloud_run \
  --project=$GOOGLE_CLOUD_PROJECT \
  --region=$GOOGLE_CLOUD_LOCATION \
  --service_name=$SERVICE_NAME \
  --with_ui \
  $AGENT_PATH


gcloud run services update $SERVICE_NAME \
    --service-account=$SERVICE_ACCOUNT \
    --region=$GOOGLE_CLOUD_LOCATION