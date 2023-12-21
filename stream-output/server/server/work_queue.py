from asyncio import Queue, ensure_future
from typing import Any, Coroutine

from typing import Coroutine

class WorkQueue():
    def __init__(self) -> None:
        self._queue: Queue[Coroutine] = Queue()
        self._worker = ensure_future(self._start())

    async def _work(self):
        task = await self._queue.get()
        try:
            await ensure_future(task)
        except Exception as e:
            print(e)
        finally:
            self._queue.task_done()

    async def _start(self):
        while True:
            await self._work()

    async def flush(self):
        await self._queue.join()

    def schedule(self, workload: Coroutine[Any, Any, Any]):
        self._queue.put_nowait(workload)

    def close(self):
        self._worker.cancel()
