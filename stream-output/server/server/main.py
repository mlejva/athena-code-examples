from multiprocessing import connection
import uvicorn
import asyncio
from typing import Any, Dict

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from e2b import CodeInterpreter, ProcessMessage
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

# To keep things simple, we only
# To keep things simple, we'll have 1 sandbox and 1 websocket connection per server instance and
# We want to show how to send sandbox's output both to the client via WS and to DB, not management of multiple sandboxes and WS connections.
# connection: WebSocket = None
# sandbox: CodeInterpreter = None

# Note: Dicts aren't thread safe.
# Dict of connections belonging to active sessions
active_connections: Dict[str, WebSocket] = {}
# Dict of sandboxes belonging to active sessions
active_sandboxes: Dict[str, CodeInterpreter] = {}

# TODO
session_outputs = []


@app.get("/{user_id}/sessions")
async def read_sessions(user_id: str):
    """Returns all past sessions saved in DB for a give user"""
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
            await sess_manager.create_new_session(websocket, user_id, session_id)
        elif message_type == "code":
            code = data["code"]

            async def handle_sandbox():
                await asyncio.to_thread(sess_manager.run_code, session_id, code)

                if not sess_manager.active_connections.get(session_id):
                    await sess_manager.close_session(session_id)
                    print(f"Session '{session_id} disconnected")

            asyncio.ensure_future(handle_sandbox())    


def main():
    create_outputs_table()
    create_sessions_table()
    config = uvicorn.Config(app, loop=loop, host="0.0.0.0", port=8000)
    server = uvicorn.Server(config)
    loop.run_until_complete(server.serve())
