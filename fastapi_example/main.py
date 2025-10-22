from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google.cloud import run_v2
import time
import httpx
import google.oauth2.id_token
from google.auth.transport.requests import Request

app = FastAPI()


class DeployRequest(BaseModel):
    basic_service_name: str
    image: str
    project_id: str
    region: str = "europe-west3"
    env_vars: dict[str, str] = {}
    timeout: int = 300
    memory: str = "1Gi"
    network: str | None = "vpc-notebook-fraknfurt"
    subnet: str | None = "vpc-sub-frankfurt-cloud-run"
    service_account: str | None = (
        "adk-cloud-run@acn-daipl.iam.gserviceaccount.com"  # to change to be unique?
    )


class DeployResponse(BaseModel):
    status: str
    unique_service_name: str
    url: str


class TestConnectionRequest(BaseModel):
    agent_url: str
    endpoint: str = "/health"  # default health check endpoint
    timeout: int = 10


class TestConnectionResponse(BaseModel):
    status: str
    response_time_ms: float
    status_code: int | None = None
    message: str


class MessagePart(BaseModel):
    text: str


class NewMessage(BaseModel):
    role: str
    parts: list[MessagePart]


class RunSSEBody(BaseModel):
    appName: str
    userId: str
    sessionId: str
    newMessage: NewMessage
    streaming: bool = False
    stateDelta: dict | None = None


class RunSSERequest(BaseModel):
    agent_url: str
    runsse_body: RunSSEBody
    timeout: int = 30


class RunSSEResponse(BaseModel):
    status: str
    response_time_ms: float
    status_code: int | None = None
    message: str
    response_data: str | None = None


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

        # no permission to set service account
        # Configure service account
        # if request.service_account:
        #     service.template.service_account = request.service_account

        # Configure VPC access if network and subnet are provided
        if request.network and request.subnet:
            service.template.vpc_access = run_v2.VpcAccess(
                egress=run_v2.VpcAccess.VpcEgress.ALL_TRAFFIC,
                network_interfaces=[
                    run_v2.VpcAccess.NetworkInterface(
                        network=request.network,
                        subnetwork=request.subnet,
                    )
                ],
            )

        service.ingress = run_v2.IngressTraffic.INGRESS_TRAFFIC_INTERNAL_ONLY

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


@app.post("/test-connection", response_model=TestConnectionResponse)
async def test_connection(request: TestConnectionRequest):
    """Test connection to an ADK agent service"""
    start_time = time.time()

    try:
        async with httpx.AsyncClient(timeout=request.timeout) as client:
            url = f"{request.agent_url.rstrip('/')}{request.endpoint}"
            response = await client.get(url)

            response_time = (time.time() - start_time) * 1000

            return TestConnectionResponse(
                status="success",
                response_time_ms=round(response_time, 2),
                status_code=response.status_code,
                message=f"Connected successfully to {url}",
            )
    except httpx.TimeoutException:
        response_time = (time.time() - start_time) * 1000
        return TestConnectionResponse(
            status="timeout",
            response_time_ms=round(response_time, 2),
            message=f"Connection timeout after {request.timeout}s",
        )
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        return TestConnectionResponse(
            status="failed",
            response_time_ms=round(response_time, 2),
            message=f"Connection failed: {str(e)}",
        )


@app.post("/test-run-sse", response_model=RunSSEResponse)
async def test_run_sse(request: RunSSERequest):
    """Test the /run_sse endpoint of an ADK agent"""
    start_time = time.time()

    try:
        # Get ID token for authentication
        url = f"{request.agent_url.rstrip('/')}/run_sse"
        # Get proper ID token with audience
        auth_req = Request()
        id_token = google.oauth2.id_token.fetch_id_token(auth_req, request.agent_url)

        headers = {"Authorization": f"Bearer {id_token}"}
        payload = request.runsse_body.model_dump()

        async with httpx.AsyncClient(timeout=request.timeout) as client:
            response = await client.post(url, headers=headers, json=payload)

            response_time = (time.time() - start_time) * 1000

            return RunSSEResponse(
                status="success",
                response_time_ms=round(response_time, 2),
                status_code=response.status_code,
                message=f"Request completed with status {response.status_code}",
                response_data=response.text[:500],  # First 500 chars
            )
    except httpx.TimeoutException:
        response_time = (time.time() - start_time) * 1000
        return RunSSEResponse(
            status="timeout",
            response_time_ms=round(response_time, 2),
            message=f"Request timeout after {request.timeout}s",
        )
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        return RunSSEResponse(
            status="failed",
            response_time_ms=round(response_time, 2),
            message=f"Request failed: {str(e)}",
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
