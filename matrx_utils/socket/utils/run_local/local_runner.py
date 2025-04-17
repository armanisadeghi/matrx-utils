import asyncio
import importlib
from enum import Enum

from common import vcprint

MOCK_SID = "mock_sid"
MOCK_NAMESPACE = "/MockUserNamespace"


class Service(str, Enum):
    """Enum mapping service names to their import paths."""

    MARKDOWN_PROCESSING = "automation_matrix.processing.markdown.service.MarkdownProcessorService"


class LocalRunner:
    """Utility to run socket-based tasks locally without socket connections"""

    def __init__(self):
        self.mock_sid = MOCK_SID
        self.mock_namespace = MOCK_NAMESPACE

    async def run_by_socket_handler(self, import_path, method_name, payload):
        """Run sio event listeners with full payload and context validation"""
        pass

    async def import_service(self, service: Service):
        module_path, class_name = service.value.rsplit(".", 1)
        module = importlib.import_module(module_path)
        service_class = getattr(module, class_name)
        return service_class

    async def run_direct(self, service: Service, task_name, task_data):
        try:
            service_class = await self.import_service(service)
        except Exception:
            import traceback

            exception = traceback.format_exc()
            vcprint(title=f"Cannot import {service.value} ", color="red", data=exception)
            return

        service = service_class()

        return await service.execute_task(task_name, task_data)


# Example usage
async def main():
    """Example of how to use the LocalRunner"""
    runner = LocalRunner()

    result = await runner.run_direct(
        service=Service.MARKDOWN_PROCESSING,
        task_name="classify_markdown",
        task_data={"raw_markdown": "Sometest"},
    )

    if result:
        vcprint(
            data=result,
            title="[local runner] Task run successful",
            color="green",
            pretty=True,
        )


if __name__ == "__main__":
    asyncio.run(main())
