from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agent import CodingAgent
import uvicorn

app = FastAPI(title="Coding Agent API", version="1.0.0")

class TaskRequest(BaseModel):
    task: str
    workspace_path: str = "workspace"

class TaskResponse(BaseModel):
    result: str
    logs: list[str]

agent = CodingAgent()

@app.post("/execute-task", response_model=TaskResponse)
async def execute_task(request: TaskRequest):
    try:
        result, logs = await agent.run_task(request.task, request.workspace_path)
        return TaskResponse(result=result, logs=logs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
