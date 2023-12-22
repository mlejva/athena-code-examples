import uvicorn
import asyncio

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from server.db import (
    create_outputs_table,
    create_sessions_table,
    get_user_sessions,
    get_session_outputs,
)

from server.session_manager import SessionManager

load_dotenv()

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
sess_manager = SessionManager()


@app.get("/{user_id}/sessions")
async def read_sessions(user_id: str):
    """Returns all past sessions saved in DB for a given user"""
    return {"sessions": get_user_sessions(user_id)}


@app.get("/sessions/{session_id}")
async def get_chat_session_outputs(session_id: str):
    return {"outputs": get_session_outputs(session_id)}


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()

    print(f"Session '{session_id}' connected", websocket, websocket.client)
    async for data in websocket.iter_json():
        message_type = data["message_type"]
        if message_type == "new_session":
            user_id = data["user_id"]
            # TODO: Handle if a user reconnects to a previous session and the sandbox is still running -> user should start receiving output from the sandbox again.
            await sess_manager.ensure_session(websocket, user_id, session_id)
        elif message_type == "code":
            code = data["code"]
            # Leave the task running in background.
            # This will ensure that the code is running inside sandbox even when client is disconnected.
            asyncio.ensure_future(sess_manager.run_code(session_id, code))

    # Client got disconnected, remove the connection from active connections.
    del sess_manager.active_connections[session_id]


def main():
    create_outputs_table()
    create_sessions_table()
    config = uvicorn.Config(app, loop=loop, host="0.0.0.0", port=8000)
    server = uvicorn.Server(config)
    loop.run_until_complete(server.serve())
