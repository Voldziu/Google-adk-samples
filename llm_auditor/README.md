Pushing to Artifact Registry:


Proponuję:

{nazwa} = adk-demo-{nazwa_agenta}




docker build -t {nazwa}:latest .

gcloud auth configure-docker europe-west3-docker.pkg.dev

docker tag {nazwa}:latest europe-west3-docker.pkg.dev/{nazwa_projektu}/adk-demo/{nazwa}:latest

docker push europe-west3-docker.pkg.dev/{nazwa_projektu}/adk-demo/{nazwa}:latest




Proxy:


gcloud run services proxy {nazwa_zdeployowanego_cloud_run_service} --region=europe-west3 --port 8008