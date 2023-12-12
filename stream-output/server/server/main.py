import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket

load_dotenv()
app = FastAPI()

active_sandboxes = {}

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")

def main():
  uvicorn.run(app, host="0.0.0.0", port=8000)
