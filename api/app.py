from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from core.orchestrator import Orchestrator

app = FastAPI(
    title="GameDevCrew API",
    description="Multi-agent AI orchestration for indie game developers",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = Orchestrator()

class TaskRequest(BaseModel):
    task: str

class TaskResponse(BaseModel):
    task: str
    routed_to: str
    routing_reason: str
    results: dict

@app.get("/")
def root():
    return {"status": "GameDevCrew API is running"}

@app.post("/ask", response_model=TaskResponse)
def ask(request: TaskRequest):
    result = orchestrator.run(request.task, verbose=False)
    return result

@app.delete("/memory")
def clear_memory():
    orchestrator.memory.clear()
    return {"status": "Session memory cleared"}