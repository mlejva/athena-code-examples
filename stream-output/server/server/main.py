import uvicorn
import asyncio
from queue import Queue
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from e2b import CodeInterpreter, ProcessMessage

from server.work_queue import WorkQueue


load_dotenv()
app = FastAPI()

# To keep things simple, we'll have 1 sandbox and 1 websocket connection per server instance and
# We want to show how to send sandbox's output both to the client via WS and to DB, not management of multiple sandboxes and WS connections.
connection: WebSocket = None
sandbox: CodeInterpreter = None

wq = WorkQueue()


async def handle_workload(workload):
    print("Sending to client")
    if connection is None:
        print("Saving to DB")
    else:
        print("Sending to client")
        await connection.send_json(workload)


def handle_sandbox_stdout(out: ProcessMessage):
    # if connection is None:
    #     print("Saving to DB")
    # else:
    #     print("Sending to client")
    print("[sandbox stdout]", out.line)
    data_out = {
        "type": "stdout",
        "line": out.line,
        "timestamp": out.timestamp,
    }
    wq.schedule(
        workload=data_out,
        on_workload=handle_workload,
    )


def handle_sandbox_stderr(out: ProcessMessage):
    # if connection is None:
    #     print("Saving to DB")
    # else:
    #     print("Sending to client")
    print("[sandbox stderr]", out.line)
    data_out = {
        "type": "stdout",
        "line": out.line,
        "timestamp": out.timestamp,
    }
    wq.schedule(
        workload=data_out,
        on_workload=handle_workload,
    )


@app.get("/")
async def read_root():
    content = sandbox.filesystem.list("/")
    print(content)
    return {"Hello": "World"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global connection
    global wq

    await websocket.accept()

    connection = websocket

    print("Client connected", websocket, websocket.client)
    try:
        while True:
            data_in = await websocket.receive_json()
            command = data_in["command"]
            print("Received command", command)
            sandbox.run_python(command)
            print("Command executed")
    except WebSocketDisconnect:
        # TODO: Redirect sandbox's stdout and stderr to DB
        print("Disconnected")
        connection = None


def main():
    global sandbox
    sandbox = CodeInterpreter(
        on_stdout=handle_sandbox_stdout,
        on_stderr=handle_sandbox_stderr,
    )

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(wq._start())

    config = uvicorn.Config(app, loop=loop, host="0.0.0.0", port=8000)
    server = uvicorn.Server(config)
    loop.run_until_complete(server.serve())
