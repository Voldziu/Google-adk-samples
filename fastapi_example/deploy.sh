gcloud run deploy adk-demo-fastapi-server \
  --image=europe-west3-docker.pkg.dev/acn-daipl/adk-demo/adk-demo-fastapi-server:latest \
  --region=europe-west3 \
  --service-account=genai-assest-backend@acn-daipl.iam.gserviceaccount.com \
  --network=vpc-notebook-fraknfurt \
  --subnet=vpc-sub-frankfurt-cloud-run




# For local testing

# docker build -t your-image:latest .




# docker run -p 8080:8080 \
#   -v ~/.config/gcloud:/root/.config/gcloud \
#   your-image:latest