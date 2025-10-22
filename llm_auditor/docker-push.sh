
docker build -t adk-demo-llm-auditor:latest .

gcloud auth configure-docker europe-west3-docker.pkg.dev

docker tag adk-demo-llm-auditor:latest europe-west3-docker.pkg.dev/acn-daipl/adk-demo/adk-demo-llm-auditor:latest

docker push europe-west3-docker.pkg.dev/acn-daipl/adk-demo/adk-demo-llm-auditor:latest