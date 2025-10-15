This repository consists of three multi-agent systems.

To run each agent, use the following commands:

```bash
cd {agent-name}
source .venv/bin/activate
adk web
```

Replace `{agent-name}` with the name of the agent you want to run.



## To deploy. Make sure you have done *google auth login* first. 
Need to have UV installed.

```bash
cd {agent-name}
source .venv/bin/activate
./deploy.sh
```


## Then, proxy the Cloud Run service to your terminal
Need to install first
*sudo apt-get install google-cloud-cli-cloud-run-proxy*

```bash
cd {agent-name}

gcloud run services proxy adk-demo-{agent-name} --region=europe-west3 --port {PORT}
```


## Frontend in progress..