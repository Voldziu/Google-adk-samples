gcloud functions deploy cleanup-services --runtime python311 --trigger-http

gcloud scheduler jobs create http cleanup-job \
  --schedule="0 * * * *" \
  --uri="https://REGION-PROJECT.cloudfunctions.net/cleanup-services" \
  --http-method=GET
  