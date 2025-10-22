
docker build -t adk-demo-fastapi-server:latest .

gcloud auth configure-docker europe-west3-docker.pkg.dev

docker tag adk-demo-fastapi-server:latest europe-west3-docker.pkg.dev/acn-daipl/adk-demo/adk-demo-fastapi-server:latest

docker push europe-west3-docker.pkg.dev/acn-daipl/adk-demo/adk-demo-fastapi-server:latest