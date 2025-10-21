gcloud run deploy deployer-service \
  --image=YOUR_IMAGE \
  --region=europe-west3 \
  --service-account=SERVICE_ACCOUNT_WITH_CLOUD_RUN_ADMIN_ROLE




# For local testing

# docker build -t your-image:latest .




# docker run -p 8080:8080 \
#   -v ~/.config/gcloud:/root/.config/gcloud \
#   your-image:latest