# matrx_utils\core\task_queue.py
import asyncio
import threading
import time
import warnings
import traceback
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Callable, Optional
from concurrent.futures import ThreadPoolExecutor
from matrx_utils import vcprint
from matrx_utils.conf import settings

# Ensure warnings are shown
warnings.filterwarnings('always')



@dataclass
class Task:
    service_name: Optional[str] = None
    user_id: str = "system"
    priority: int = 10
    data: Optional[dict] = None
    sid: Optional[str] = None
    namespace: Optional[str] = None
    stream_handler: Optional[Callable] = None
    is_sync: bool = False
    callback: Optional[Callable] = None

    def __post_init__(self):
        self.submit_time = getattr(self, "submit_time", time.time())

    def __lt__(self, other):
        return (self.priority, self.submit_time) < (other.priority, other.submit_time)

class TaskQueue:
    _instance = None
    _lock = threading.Lock()

    @classmethod
    def get_instance(cls) -> 'TaskQueue':
        """Get singleton instance, initializing if needed."""
        return get_task_queue()

    @classmethod
    async def get_instance_async(cls) -> 'TaskQueue':
        """Async method to get singleton."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, cls.get_instance)

    @classmethod
    def initialize(cls, user_sessions=None):
        """Initialize singleton with optional user_sessions for testing."""
        from matrx_utils.socket.core.user_sessions import get_user_session_namespace

        with cls._lock:
            if cls._instance is None:
                user_sessions = user_sessions or get_user_session_namespace()
                cls._instance = cls(user_sessions)
                loop = asyncio.get_event_loop()
                asyncio.create_task(cls._instance.start())
                vcprint("[TASK QUEUE] Initialized", color="green")
            return cls._instance

    @classmethod
    def reset(cls):
        """Reset singleton for testing."""
        with cls._lock:
            if cls._instance:
                asyncio.create_task(cls._instance.shutdown())
            cls._instance = None
            vcprint("[TASK QUEUE] Reset", color="yellow")

    def __init__(self, user_sessions):
        self.user_sessions = user_sessions
        self.queue = asyncio.PriorityQueue()
        self.background_queue = asyncio.PriorityQueue()
        self.queue_lock = asyncio.Lock()
        self.user_tasks = defaultdict(int)
        self.user_limits = defaultdict(lambda: 5)
        self.system_service_factory = None
        self.short_running_workers = 10
        self.long_running_workers = 5
        self.running = True
        self.executor = ThreadPoolExecutor(max_workers=4)

    def set_user_limit(self, user_id: str, limit: int):
        self.user_limits[user_id] = max(0, limit)

    async def add_task(self, task: Task):
        async with self.queue_lock:
            if task.user_id != "system" and self.user_tasks[task.user_id] >= self.user_limits[task.user_id]:
                vcprint(
                    data=f"[TASK QUEUE] Throttling user {task.user_id}: too many tasks",
                    color="yellow",
                )
                raise ValueError(f"User {task.user_id} exceeded task limit")
            await self.queue.put(task)
            vcprint(
                data=f"[TASK QUEUE] Added task | Service: {task.service_name} | User: {task.user_id} | Priority: {task.priority}",
                color="green",
            )

    def add_task_sync(self, task: Task):
        loop = asyncio.get_event_loop()
        try:
            if loop.is_running():
                future = asyncio.run_coroutine_threadsafe(self.add_task(task), loop)
                future.result()
            else:
                asyncio.run(self.add_task(task))
        except Exception as e:
            print(f"[TASK QUEUE] Error in add_task_sync: {str(e)}")
            traceback.print_exc()

    async def add_background_task(self, **kwargs):
        async with self.queue_lock:
            task = Task(priority=100, **kwargs)
            if task.user_id != "system" and self.user_tasks[task.user_id] >= self.user_limits[task.user_id]:
                vcprint(
                    data=f"[TASK QUEUE] Throttling user {task.user_id}: too many background tasks",
                    color="yellow",
                )
                raise ValueError(f"User {task.user_id} exceeded task limit")
            await self.background_queue.put(task)
            vcprint(
                data=f"[TASK QUEUE] Added background task | Service: {task.service_name} | User: {task.user_id}",
                color="cyan",
            )

    def add_background_task_sync(self, **kwargs):
        loop = asyncio.get_event_loop()
        try:
            if loop.is_running():
                future = asyncio.run_coroutine_threadsafe(self.add_background_task(**kwargs), loop)
                future.result()
            else:
                asyncio.run(self.add_background_task(**kwargs))
        except Exception as e:
            print(f"[TASK QUEUE] Error in add_background_task_sync: {str(e)}")
            traceback.print_exc()

    async def get_task(self) -> Optional[Task]:
        while self.running:
            try:
                task = await asyncio.wait_for(self.queue.get(), timeout=1.0)
                async with self.queue_lock:
                    self.user_tasks[task.user_id] += 1
                return task
            except asyncio.TimeoutError:
                try:
                    task = await asyncio.wait_for(self.background_queue.get(), timeout=1.0)
                    async with self.queue_lock:
                        self.user_tasks[task.user_id] += 1
                    return task
                except asyncio.TimeoutError:
                    continue
            except Exception as e:
                print(f"[TASK QUEUE] Error in get_task: {str(e)}")
                traceback.print_exc()
        return None

    async def complete_task(self, task: Task):
        try:
            async with self.queue_lock:
                self.user_tasks[task.user_id] = max(0, self.user_tasks[task.user_id] - 1)
                vcprint(
                    data=f"[TASK QUEUE] Completed task | Service: {task.service_name} | User: {task.user_id}",
                    color="blue",
                )
        except Exception as e:
            print(f"[TASK QUEUE] Error in complete_task: {str(e)}")
            traceback.print_exc()

    async def worker(self, worker_type: str):
        loop = asyncio.get_running_loop()
        while self.running:
            try:
                task = await self.get_task()
                if not task:
                    break
                try:
                    is_long_running = task.service_name in settings.LONG_RUNNING_SERVICES if task.service_name else False
                    if worker_type == "short" and is_long_running:
                        await self.queue.put(task)
                        async with self.queue_lock:
                            self.user_tasks[task.user_id] -= 1
                        continue
                    elif worker_type == "long" and not is_long_running and task.service_name:
                        await self.queue.put(task)
                        async with self.queue_lock:
                            self.user_tasks[task.user_id] -= 1
                        continue

                    if task.callback:
                        if task.is_sync:
                            def sync_callback():
                                try:
                                    return task.callback(task.data)
                                except Exception as e:
                                    print(f"[TASK QUEUE] Error in sync callback: {str(e)}")
                                    traceback.print_exc()
                            await loop.run_in_executor(self.executor, sync_callback)
                        else:
                            await task.callback(task.data)
                    elif task.service_name:
                        if task.sid:
                            user_id, service_factory = await self.user_sessions.get_user_factory_and_id(task.sid)
                            if not service_factory:
                                raise ValueError(f"No ServiceFactory for SID {task.sid}")
                            await service_factory.process_request(
                                sid=task.sid,
                                user_id=user_id,
                                data=task.data or {},
                                namespace=task.namespace or "/UserSession",
                                service_name=task.service_name
                            )
                        else:
                            if task.user_id != "system":
                                service_factory = self.user_sessions.user_service_factories.get(task.user_id)
                            else:
                                if not self.system_service_factory:
                                    from matrx_utils.socket.core.app_factory import AppServiceFactory
                                    self.system_service_factory = AppServiceFactory()
                                service_factory = self.system_service_factory
                            if not service_factory:
                                raise ValueError(f"No ServiceFactory for user {task.user_id}")
                            service = service_factory.create_service(task.service_name)
                            if hasattr(service, "stream_handler"):
                                service.stream_handler = task.stream_handler
                            if hasattr(service, "user_id"):
                                service.user_id = task.user_id
                            if task.is_sync:
                                def sync_process():
                                    try:
                                        return service.process_task(task.data or {}, context={"namespace": task.namespace})
                                    except Exception as e:
                                        print(f"[TASK QUEUE] Error in sync process: {str(e)}")
                                        traceback.print_exc()
                                await loop.run_in_executor(self.executor, sync_process)
                            else:
                                await service.process_task(task.data or {}, context={"namespace": task.namespace})

                except Exception as e:
                    print(f"[TASK QUEUE] Error processing task | Service {task.service_name} | User {task.user_id} | Error={str(e)}")
                    traceback.print_exc()
                finally:
                    await self.complete_task(task)
            except Exception as e:
                print(f"[TASK QUEUE] Error in worker {worker_type}: {str(e)}")
                traceback.print_exc()

    async def start(self):
        try:
            short_tasks = [
                asyncio.create_task(self.worker("short"))
                for _ in range(self.short_running_workers)
            ]
            long_tasks = [
                asyncio.create_task(self.worker("long"))
                for _ in range(self.long_running_workers)
            ]
            self._worker_tasks = short_tasks + long_tasks
        except Exception as e:
            print(f"[TASK QUEUE] Error in start: {str(e)}")
            traceback.print_exc()

    async def shutdown(self):
        try:
            self.running = False
            if hasattr(self, "_worker_tasks"):
                for task in self._worker_tasks:
                    task.cancel()
                await asyncio.gather(*self._worker_tasks, return_exceptions=True)
            self.executor.shutdown(wait=True)
            vcprint("[TASK QUEUE] Shutdown complete", color="green")
        except Exception as e:
            print(f"[TASK QUEUE] Error in shutdown: {str(e)}")
            traceback.print_exc()

_task_queue_instance = None

def get_task_queue():
    """Get or initialize TaskQueue singleton."""
    global _task_queue_instance
    with threading.Lock():
        if _task_queue_instance is None:
            _task_queue_instance = TaskQueue.initialize()
        return _task_queue_instance
