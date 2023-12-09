import logging
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi import FastAPI
from dotenv import load_dotenv
from e2b import Sandbox

# You can enable detailed logging for E2B with DEBUG level:
# logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.INFO)

load_dotenv()

app = FastAPI()

# We keep a dictionary of active sandboxes in memory.
# As long as the sandbox objects are in the memory, they are pinging the E2B servers to keep them alive.
# Keep in mind that E2B sandbox won't close (and stays alive on our servers) if you don't close it explicitly via `sandbox.close()`.
# To close sandboxes automatically after a certain time, please take a look at https://e2b.dev/docs/sandbox/api/reconnect - the logic of the server would be a little different though.
active_sandboxes = {}

@app.post("/session")
async def create_session():
  """
  Creates a new session.
  """
  try:
    sandbox = Sandbox(
      # You can register callbacks to listen to stdout and stderr
      # of any process inside the sandbox that you start via `sandbox.process.start()`
      on_stderr=lambda output: print("[stderr from sandbox]", output.line),
      on_stdout=lambda output: print("[stdout from sandbox]", output.line),
    )
    active_sandboxes[sandbox.id] = sandbox
  except Exception as e:
    print(f"Error in create_session: {str(e)}")
    raise HTTPException(status_code=500, detail=str(e))

  print(active_sandboxes)
  return {"status": "Session created", "session_id": sandbox.id}

@app.get("/session/{session_id:str}")
async def get_session(session_id: str):
  """
  Retrieves a session by its ID.
  """
  sandbox = active_sandboxes.get(session_id)
  if not sandbox:
    raise HTTPException(status_code=404, detail="Session not found")
  return {"status": "Session found", "session_id": sandbox.id}

@app.delete("/session/{session_id:str}")
async def close_session(session_id: str):
  """
  Closes a session by its ID.
  """
  try:
    sandbox = active_sandboxes.get(session_id)
    if not sandbox:
      raise HTTPException(status_code=404, detail="Session not found")
    else:
      sandbox.close()
      active_sandboxes.pop(session_id)
      return {"status": "Session closed", "session_id": session_id}

  except Exception as e:
    print(f"Error in close_session: {str(e)}")
    raise HTTPException(status_code=500, detail=str(e))

def main():
  uvicorn.run(app, host="0.0.0.0", port=8000)