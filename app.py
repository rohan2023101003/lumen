import os
import traceback
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent import LumenAgent
from fastapi.responses import FileResponse

app = FastAPI(title="Lumen AI Gateway")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Agent
try:
    agent_instance = LumenAgent()
except Exception as e:
    print(f"❌ Failed to initialize Agent: {e}")

class AgentRequest(BaseModel):
    user_id: str
    user_request: str

@app.post("/query")
async def run_agent(req: AgentRequest):
    try:
        inputs = {
            "user_id": req.user_id,
            "user_request": req.user_request,
            "data_pool": {},
            "next_step": "",
            "final_output": "",
            "visited": []
        }
        
        # Run the graph
        result = agent_instance.graph.invoke(inputs)
        
        # Ensure we return strings even if keys are missing
        return {
            "output": result.get("final_output", "No output generated"),
            "flow": result.get("visited", [])
        }
    except Exception as e:
        # THIS WILL PRINT THE ACTUAL ERROR TO YOUR TERMINAL
        print("--- AGENT ERROR START ---")
        traceback.print_exc() 
        print("--- AGENT ERROR END ---")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def read_index():
    return FileResponse('index.html')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)