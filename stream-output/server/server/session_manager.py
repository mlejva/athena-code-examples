import asyncio

from typing import Dict, Any
from fastapi import WebSocket
from e2b import CodeInterpreter, ProcessMessage

from server.work_queue import WorkQueue
from server.db import (
    insert_outputs,
    create_session,
)


class SessionManager:
    def __init__(self) -> None:
        self.active_connections: Dict[str, WebSocket] = {}
        self.active_sandboxes: Dict[str, CodeInterpreter] = {}
        self.session_outputs: Dict[str, list[Dict[str, Any]]] = {}
        self.wq = WorkQueue()

    async def _stream_output(self, session_id: str, output: ProcessMessage, type: str):
        print(f"[sandbox {type}]", output)
        serialized_output = {
            "message_type": "process_output",
            "type": type,
            "line": output.line,
            "timestamp": output.timestamp,
        }

        # Append the list of outputs that we keep in the memory and save it to DB
        if self.session_outputs.get(session_id) is None:
            self.session_outputs[session_id] = [serialized_output]
        else:
            self.session_outputs[session_id].append(serialized_output)

        insert_outputs(session_id, self.session_outputs[session_id])

        connection = self.active_connections.get(session_id)

        # If client is connected, send output to the client
        if connection is not None:
            await connection.send_json(serialized_output)

    async def _create_new_session(
        self, connection: WebSocket, user_id: str, session_id: str
    ):
        create_session(user_id, session_id)
        print("creating new session", connection)
        self.active_connections[session_id] = connection
        print("active_connections", self.active_connections)

        sandbox = self.active_sandboxes.get(session_id)
        # In case there's already s sandbox, we want to close it first. This case shouldn't ever happen though.
        if sandbox is not None:
            sandbox.close()
        self.active_sandboxes[session_id] = CodeInterpreter(
            on_stdout=lambda out: self.wq.schedule(
                self._stream_output(session_id, out, "stdout")
            ),
            on_stderr=lambda out: self.wq.schedule(
                self._stream_output(session_id, out, "stderr")
            ),
        )

        print(f"User '{user_id}' connected, starting a new session", session_id)
        await connection.send_json({"status": "session_created"})

    async def ensure_session(
        self, connection: WebSocket, user_id: str, session_id: str
    ):
        """Either creates a new session for a user or reconnects the user to an existing previous session."""

        # If there's an existing sandbox for `session_id`, user is reconnecting to a previous session.
        #   - We want to start sending the sandbox's output to the client.
        # Else, we just create a new session for the user.
        if (self.active_sandboxes.get(session_id)) is None:
            await self._create_new_session(connection, user_id, session_id)
        else:
            # Since the sandbox exists, self.close_session() was never called, all we need to do is save the connection under this session id.
            self.active_connections[session_id] = connection

    async def run_code(self, session_id: str, code: str):
        sandbox = self.active_sandboxes.get(session_id)
        if sandbox is None:
            raise Exception(
                f"Cannot run command - sandbox for session '{session_id}' not found"
            )

        print("Received code", code)
        # We move run_python to a thread to avoid blocking the event loop
        # because `run_python` is a synchronous operation.
        await asyncio.to_thread(sandbox.run_python, code)
        print("Code executed")

        # When we finish running code, we check if there's an active client connection.
        # If not, we close the sandbox.
        if not self.active_connections.get(session_id):
            await self.close_session(session_id)
            print(f"Session '{session_id} disconnected")

    async def close_session(self, session_id: str):
        if (self.active_connections.get(session_id)) is not None:
            del self.active_connections[session_id]
        if (self.session_outputs.get(session_id)) is not None:
            del self.session_outputs[session_id]

        sandbox = self.active_sandboxes.get(session_id)
        if sandbox is not None:
            del self.active_sandboxes[session_id]
            sandbox.close()
