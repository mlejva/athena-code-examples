import uvicorn
import asyncio

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from e2b import CodeInterpreter, ProcessMessage

from server.work_queue import WorkQueue

load_dotenv()

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

async def handle_workload(workload):
    print("Sending to client")
    if connection is None:
        print("Saving to DB")
    else:
        print("Sending to client")
        await connection.send_json(workload)

def handle_sandbox_stdout(out: ProcessMessage):
    print("[sandbox stdout]", out.line)
    data_out = {
        "type": "stdout",
        "line": out.line,
        "timestamp": out.timestamp,
    }
    wq.schedule(handle_workload(data_out))

def handle_sandbox_stderr(out: ProcessMessage):
    print("[sandbox stderr]", out.line)
    data_out = {
        "type": "stdout",
        "line": out.line,
        "timestamp": out.timestamp,
    }
    wq.schedule(handle_workload(data_out))

app = FastAPI()
wq = WorkQueue()

# To keep things simple, we'll have 1 sandbox and 1 websocket connection per server instance and
# We want to show how to send sandbox's output both to the client via WS and to DB, not management of multiple sandboxes and WS connections.
connection: WebSocket = None
sandbox = CodeInterpreter(
    on_stdout=handle_sandbox_stdout,
    on_stderr=handle_sandbox_stderr,
)

@app.get("/")
async def read_root():
    content = sandbox.filesystem.list("/")
    print(content)
    return {"Hello": "World"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global connection

    await websocket.accept()
    connection = websocket

    print("Client connected", websocket, websocket.client)
    try:
        async for data in websocket.iter_json():
            command = data["command"]
            print("Received command", command)
            sandbox.run_python(command)
            print("Command executed")
    except WebSocketDisconnect:
        # TODO: Redirect sandbox's stdout and stderr to DB
        print("Disconnected")
        connection = None

def main():
    config = uvicorn.Config(app, loop=loop, host="0.0.0.0", port=8000)
    server = uvicorn.Server(config)

    loop.run_until_complete(server.serve())
