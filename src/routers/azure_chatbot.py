from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

import os, io, time

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
    project_endpoint = _env("AZURE_EXISTING_AIPROJECT_ENDPOINT")
    agent_id = _env("AZURE_EXISTING_AGENT_ID")

    project_client = AIProjectClient(
        endpoint=project_endpoint,
        credential=DefaultAzureCredential(),
    )

    agent = project_client.agents.get(agent_name=agent_id)

    openai_client = project_client.get_openai_client()

    try:
        resp = openai_client.responses.create(
            input=[{"role": "user", "content": request.message}],
            extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    text = getattr(resp, "output_text", None)
    if not text:
        raise HTTPException(status_code=500, detail="No output_text in response (check SDK response shape).")

    return ChatResponse(response=text, status="success")

class UploadResponse(BaseModel):
    file_id: str
    vector_store_id: str
    vector_store_file_id: str
    status: str

def _get_openai_client():
    project_endpoint = _env("AZURE_EXISTING_AIPROJECT_ENDPOINT")
    project_client = AIProjectClient(
        endpoint=project_endpoint,
        credential=DefaultAzureCredential(),
    )
    return project_client.get_openai_client()


@router.get("/agent/vectorstore/list")
def list_vector_stores():
    openai_client = _get_openai_client()
    vs_list = openai_client.vector_stores.list(limit=100)
    return [{"id": vs.id, "name": vs.name} for vs in vs_list.data]


@router.post("/agent/vectorstore/upload", response_model=UploadResponse)
async def upload_to_agent_vector_store(file: UploadFile = File(...)) -> UploadResponse:
    vector_store_id = _env("AZURE_AGENT_VECTOR_STORE_ID")
    openai_client = _get_openai_client()

    # 1) upload file to Files
    content = await file.read()
    buf = io.BytesIO(content)
    buf.name = file.filename

    uploaded = openai_client.files.create(file=buf, purpose="assistants")
    file_id = uploaded.id

    # 2) attach file to vector store (indexing starts)
    vs_file = openai_client.vector_stores.files.create(
        vector_store_id=vector_store_id,
        file_id=file_id,
    )
    vs_file_id = vs_file.id
    print("Started indexing, vector store file ID:", vs_file)
    status = getattr(vs_file, "status", "in_progress")

    # 3) poll status
    for _ in range(60):
        cur = openai_client.vector_stores.files.retrieve(
            vector_store_id=vector_store_id,
            file_id=vs_file_id, 
        )
        status = cur.status
        if status in ("completed", "failed", "cancelled"):
            break
        time.sleep(1)

    if status != "completed":
        raise HTTPException(status_code=500, detail=f"Indexing not completed. Status={status}")

    return UploadResponse(
        file_id=file_id,
        vector_store_id=vector_store_id,
        vector_store_file_id=vs_file_id,
        status=status,
    )