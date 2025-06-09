from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from update_agent import handle_update

app = FastAPI()

# Allow requests from your frontend (adjust allow_origins later for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "AI Agent backend is running."}

@app.post("/update")
async def update_portfolio(request: Request):
    data = await request.json()
    command = data.get("command")
    if not command:
        return {"status": "error", "message": "Missing command"}

    result = handle_update(command)
    return {"status": "success", "message": result}
