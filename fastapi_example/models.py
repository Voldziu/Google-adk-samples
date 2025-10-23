from pydantic import BaseModel, model_validator
from typing import Optional


class FrontendRequest(BaseModel):
    user_email: str = (
        "mikolaj.machalski@accenture.com"  # MOCKED, TO BE GET FROM FRONTEND
    )
    agent_name: str


class DeployRequest(FrontendRequest):
    pass


class DeployResponse(BaseModel):
    status: str
    unique_service_name: str
    url: str


# move all deployment parameters to env, for deployment
class DeployRequestInner(BaseModel):
    agent_name: str
    image: str = ""
    project_id: str = "acn-daipl"  # TO BE MOVED TO ENV VAR
    region: str = "europe-west3"
    env_vars: dict[str, str] = {}
    timeout: int = 300
    memory: str = "1Gi"
    network: str | None = "vpc-notebook-fraknfurt"
    subnet: str | None = "vpc-sub-frankfurt-cloud-run"
    service_account: str | None = (
        "adk-cloud-run@acn-daipl.iam.gserviceaccount.com"  # to change to be unique?
    )

    @model_validator(mode="after")
    def set_image(self):
        if not self.image:
            agent_name_formatted = self.agent_name.replace("_", "-")
            self.image = f"europe-west3-docker.pkg.dev/acn-daipl/adk-demo/adk-demo-{agent_name_formatted}:latest"  # assume that docker image is built with that nam
        return self


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


class QueryRequest(BaseModel):
    auth: FrontendRequest
    query: str
    current_session_id: str | None = None
    timeout: int = 300


class AgentAnswerPart(BaseModel):
    agent_name: str
    text: str


class QueryResponse(BaseModel):
    success: bool
    query: str
    answer: list[AgentAnswerPart]
    error: Optional[str] = None
