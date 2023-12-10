# Long running sessions with E2B sandboxes

This example contains a FastAPI server that keeps a dictionary of active E2B sandboxes in the memory.
As long as the sandboxes are in the memory and `sandbox.close()` is ***not*** called, the sandboxes stay alive.

The code is commented but please do let us know if you have any questions.

The full code is in [`main.py`](./long_running_sessions/main.py).

## Run the example
1. Copy `.env.example` to `.env`
1. Get your E2B API key [here](https://e2b.dev/docs/getting-started/api-key) and paste it in the `.env` file
1. Install the dependencies:
    ```bash
    poetry install
    ```
1. Start the server:
    ```bash
    poetry run start
    ```