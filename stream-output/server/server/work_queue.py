# from concurrent.futures import ThreadPoolExecutor
from asyncio import Queue, ensure_future, create_task, new_event_loop
from typing import Any, Callable, Coroutine, Generic, TypeVar

from typing import Coroutine

T = TypeVar("T")


class WorkQueue(Generic[T]):
    """Queue that tries to always process only the most recently scheduled workload."""

    def __init__(self) -> None:
        self._queue: Queue[Coroutine] = Queue()
        # self._on_workload = on_workload
        # self._loop = new_event_loop()
        # self._worker = ensure_future(self._start())

        # executor = ThreadPoolExecutor()
        # self._refreshing_task = executor.submit(self._start)

    # def __init__(self, on_workload: Callable[[T], Coroutine[Any, Any, Any]]) -> None:
    #     self._queue: Queue[Coroutine] = Queue()
    #     self._on_workload = on_workload
    #     self._worker = ensure_future(self._start())

    async def _work(self):
        print("Waiting for work")
        # Save the newest log to the db or wait until a log is pushed to the queue and then save it to the db.
        task = await self._queue.get()
        print("Got work")
        try:
            await ensure_future(task)
        except Exception as e:
            print(e)
        finally:
            self._queue.task_done()

    async def _start(self):
        with open("work_queue.txt", "a") as f:
            f.write("start\n")
        print("Started work queue")
        while True:
            await self._work()

    async def flush(self):
        await self._queue.join()

    def schedule(
        self, workload: T, on_workload: Callable[[T], Coroutine[Any, Any, Any]]
    ):
        task = on_workload(workload)
        self._queue.put_nowait(task)

    def close(self):
        self._worker.cancel()
