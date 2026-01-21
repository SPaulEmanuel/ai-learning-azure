from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import ListSortOrder
import os

router = APIRouter()

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)

class ChatResponse(BaseModel):
    response: str
    status: str

def _env(name: str) -> str:
    v = os.getenv(name)
    if not v:
        raise HTTPException(status_code=500, detail=f"Missing env var: {name}")
    return v

@router.post("/chat/azure-agent", response_model=ChatResponse)
def chat_with_azure_agent(request: ChatRequest) -> ChatResponse:
    project_endpoint = _env("AZURE_FOUNDRY_PROJECT_ENDPOINT") 
    agent_id = _env("AZURE_OPENAI_AGENT_ID")

    project = AIProjectClient(
        credential=DefaultAzureCredential(),
        endpoint=project_endpoint
    )

    thread = project.agents.threads.create()

    project.agents.messages.create(
        thread_id=thread.id,
        role="user",
        content=request.message
    )

    run = project.agents.runs.create_and_process(
        thread_id=thread.id,
        agent_id=agent_id
    )

    if run.status == "failed":
        raise HTTPException(status_code=502, detail=f"Run failed: {run.last_error}")

    messages = project.agents.messages.list(
        thread_id=thread.id,
        order=ListSortOrder.DESCENDING
    )

    # găsește primul mesaj de la assistant
    for m in messages:
        if m.role == "assistant" and m.text_messages:
            return ChatResponse(response=m.text_messages[-1].text.value, status="success")

    raise HTTPException(status_code=502, detail="No assistant message returned")
