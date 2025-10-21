from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google.cloud import run_v2
import time

app = FastAPI()


class DeployRequest(BaseModel):
    basic_service_name: str
    image: str
    project_id: str
    region: str = "europe-west3"
    env_vars: dict[str, str] = {}
    timeout: int = 300
    memory: str = "1Gi"


class DeployResponse(BaseModel):
    status: str
    unique_service_name: str
    url: str


def generate_service_name(basic_service_name: str) -> str:

    timestamp = int(time.time())
    return f"{basic_service_name}-{timestamp}"


@app.post("/deploy", response_model=DeployResponse)
async def deploy_service(
    request: DeployRequest,
):

    try:
        client = run_v2.ServicesClient()
        service = run_v2.Service()
        service.template.containers = [
            run_v2.Container(
                image=request.image,
                env=[
                    run_v2.EnvVar(name=k, value=v) for k, v in request.env_vars.items()
                ],
                resources=run_v2.ResourceRequirements(
                    limits={"memory": request.memory}
                ),
            )
        ]
        service.template.timeout = f"{request.timeout}s"

        parent = f"projects/{request.project_id}/locations/{request.region}"

        # Deploy or update the service
        operation = client.create_service(
            parent=parent,
            service=service,
            service_id=generate_service_name(request.basic_service_name),
        )

        response = operation.result()

        return DeployResponse(
            status="Deployed", unique_service_name=response.name, url=response.uri
        )
    except Exception as e:
        return DeployResponse(
            status=f"Failed: {str(e)}", unique_service_name="", url=""
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
