import asyncio
from matrx_utils.common import vcprint
from matrx_utils.socket.core.request_base import SocketRequestBase
from ..services.log_service import LogService


class ServiceFactory:
    def __init__(self):
        self.services = {}
        self.service_instances = {}
        self.multi_instance_services = set()
        self.register_default_services()

    def register_service(self, service_name, service_class):
        self.services[service_name] = service_class

    def register_multi_instance_service(self, service_name, service_class):
        self.services[service_name] = service_class
        self.multi_instance_services.add(service_name)

    def create_service(self, service_name, force_new=False):
        if service_name not in self.services:
            raise ValueError(f"Unknown service type: {service_name}")

        if service_name in self.multi_instance_services or force_new:
            vcprint(
                verbose=True,
                data=f"[ServiceFactory] Creating new instance of {service_name}",
                color="green",
            )
            return self.services[service_name]()

        if service_name not in self.service_instances:
            self.service_instances[service_name] = self.services[service_name]()
            vcprint(
                verbose=True,
                data=f"[ServiceFactory] Created new instance of {service_name}",
                color="green",
            )
        else:
            vcprint(
                verbose=True,
                data=f"[ServiceFactory] Reusing existing instance of {service_name}",
                color="blue",
            )
        return self.service_instances[service_name]

    def register_default_services(self):
        self.register_service("log_service", LogService)
        """Register services here."""

    async def process_request(self, sid, user_id, data, namespace, service_name):
        request = SocketRequestBase(sid, data, namespace, service_name, user_id)
        success, prepared_tasks = await request.initialize()

        if success:
            tasks = []
            temp_instances = []
            for task_info in prepared_tasks:
                vcprint(task_info, title="Task Info", color="green")

                force_new = service_name in self.multi_instance_services
                service_instance = self.create_service(service_name, force_new=force_new)

                if force_new:
                    temp_instances.append(service_instance)

                service_instance.add_stream_handler(task_info["stream_handler"])
                service_instance.set_user_id(user_id)

                if "log_level" in task_info and task_info["log_level"] is not None and task_info["log_level"] != "":
                    service_instance.set_log_level(task_info["log_level"])

                tasks.append(service_instance.process_task(task_info["task"], task_info["context"]))

            await asyncio.gather(*tasks)

            for instance in temp_instances:
                if hasattr(instance, "cleanup"):
                    await instance.cleanup()
                del instance

        return self.create_service(service_name)
