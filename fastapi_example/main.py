from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import run_v2
import logging
import json
import hashlib
import time
import httpx
import google.oauth2.id_token
from google.auth.transport.requests import Request

from models import (
    DeployRequest,
    DeployRequestInner,
    DeployResponse,
    TestConnectionRequest,
    TestConnectionResponse,
    QueryRequest,
    QueryResponse,
    RunSSEBody,
    NewMessage,
    MessagePart,
    AgentAnswerPart,
)


from mock_db import DB_ENV_VARS, DB


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def generate_service_name(basic_service_name: str) -> str:

    timestamp = int(time.time())
    return f"{basic_service_name}-{timestamp}"


def get_env_vars_for_agent(agent_name: str) -> dict[str, str]:
    # Placeholder function to get environment variables from a database
    return DB_ENV_VARS.get(agent_name, {})


@app.post("/deploy", response_model=DeployResponse)
async def deploy_endpoint(request: DeployRequest):
    env_vars = get_env_vars_for_agent(request.agent_name)

    deploy_request_inner = DeployRequestInner(
        agent_name=request.agent_name, env_vars=env_vars
    )

    return await deploy_service(deploy_request_inner, user_email=request.user_email)


def save_to_db(user_email: str, agent_name: str, agent_url: str):
    # Placeholder function to save to a database
    DB[(user_email, agent_name)] = agent_url
    logger.info(f"Saved to DB: {agent_name} -> {agent_url}")


async def deploy_service(request: DeployRequestInner, user_email: str):

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

        # service.ingress = run_v2.IngressTraffic.INGRESS_TRAFFIC_INTERNAL_ONLY

        parent = f"projects/{request.project_id}/locations/{request.region}"

        # Deploy or update the service
        operation = client.create_service(
            parent=parent,
            service=service,
            service_id=generate_service_name(request.agent_name),
        )

        response = operation.result()

        save_to_db(user_email, request.agent_name, response.uri)

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


def authorize_url(agent_url: str) -> str:
    """Authorize the request using Google ID token"""

    auth_req = Request()
    id_token = google.oauth2.id_token.fetch_id_token(auth_req, agent_url)
    return id_token


def call_db_for_agent_url(user_email: str, agent_name: str) -> str:
    """Fetch agent URL from the mock database"""
    return DB.get((user_email, agent_name), "")


def email_to_id(user_email):
    return hashlib.sha256(user_email.lower().encode()).hexdigest()


def generate_session_id():
    return hashlib.sha256(str(time.time()).encode()).hexdigest()


# TODO: Check if session exists, and then create (get endpoint on agent side)
async def create_session_for_user(user_email: str, agent_name: str) -> str:
    """Create a unique session ID for the user-agent pair"""
    agent_url = call_db_for_agent_url(user_email=user_email, agent_name=agent_name)
    # user_id = email_to_id(user_email)
    user_id = "user"
    session_id = generate_session_id()

    id_token = authorize_url(agent_url)
    headers = {"Authorization": f"Bearer {id_token}"}
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{agent_url}/apps/{agent_name}/users/{user_id}/sessions",
            json={"session_id": session_id, "state": {}},
            headers=headers,
        )

    return session_id


def get_runsse_body(
    agent_name: str, user_id: str, session_id: str, query: str
) -> RunSSEBody:

    runsse_body = RunSSEBody(
        appName=agent_name,
        userId=user_id,
        sessionId=session_id,
        newMessage=NewMessage(
            role="user",
            parts=[MessagePart(text=query)],
        ),
        streaming=False,
        stateDelta=None,
    )
    return runsse_body


def parse_response(response_text: str) -> list[AgentAnswerPart]:
    data = json.loads(response_text)
    agent_answer_parts: list[AgentAnswerPart] = []
    for part in data:
        agent_name = part.get("author", "")
        content = part.get("content", "")
        if content.get("role") == "model":
            parts = content.get("parts", [])
            inside_part = parts[0]  # assuming single part (only that scenario)
            if "text" in inside_part:
                agent_text = inside_part["text"]
                agent_answer_parts.append(
                    AgentAnswerPart(agent_name=agent_name, text=agent_text)
                )

    return agent_answer_parts


@app.post("/query", response_model=QueryResponse)
async def query_agent(request: QueryRequest):
    """Run /query endpoint of an ADK agent"""
    user_email = request.auth.user_email
    agent_name = request.auth.agent_name
    agent_url = call_db_for_agent_url(user_email=user_email, agent_name=agent_name)

    try:
        # Get ID token for authentication
        url = f"{agent_url.rstrip('/')}/run"
        # Get proper ID token with audience

        # user_id = email_to_id(user_email)
        user_id = "user"
        session_id = request.current_session_id or await create_session_for_user(
            user_email=user_email, agent_name=agent_name
        )
        # session_id = "6c38fa03-9ca5-488f-b52d-d9bbb6173ade" # LOCAL
        runsse_body = get_runsse_body(agent_name, user_id, session_id, request.query)
        payload = runsse_body.model_dump()

        # Comment to test locally
        id_token = authorize_url(agent_url)
        headers = {"Authorization": f"Bearer {id_token}"}
        # Comment to test locally
        async with httpx.AsyncClient(timeout=request.timeout) as client:
            response = await client.post(
                url, headers=headers, json=payload
            )  # delete headers to test locally
            response_parsed = parse_response(response.text)
            return QueryResponse(
                success=True, query=request.query, answer=response_parsed
            )
    except httpx.TimeoutException:
        return QueryResponse(
            success=False,
            query=request.query,
            answer=[],
            error="Connection timeout",
        )
    except Exception as e:
        return QueryResponse(
            success=False,
            query=request.query,
            answer=[],
            error=str(e),
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
