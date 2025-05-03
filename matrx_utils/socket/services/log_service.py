import os
import logging
from datetime import datetime
import re
import asyncio

from matrx_utils import vcprint
from matrx_utils.socket.core.service_base import SocketServiceBase
from matrx_utils.conf import settings

LOG_FILE_MAPPING = {
    "application logs": os.path.join(settings.REMOTE_LOG_DIRECTORY, settings.LOG_FILENAME),
    "daphne logs": "aidreamdev.log",  # idk if we need this anymore.
    "local logs": os.path.join(settings.LOCAL_LOG_DIRECTORY, settings.LOG_FILENAME)
}


class LogService(SocketServiceBase):
    def __init__(self, log_dir: str = "/var/log/aidream"):
        self.log_dir = log_dir
        self.logger = logging.getLogger(__name__)
        self.mic_check_message = None
        self.filename = "application logs"  # Use user-friendly name
        self.lines = 100
        self.search = None
        self.interval = 1.0
        self._tail_task = None  # Track tailing task
        self._tail_active = False  # Flag to control tailing
        self._ensure_log_dir()
        super().__init__(app_name="log_service", service_name="log_service", log_level="INFO", batch_print=False)

    async def process_task(self, task, task_context=None, process=True):
        vcprint("Log Service Processing Task")
        return await self.execute_task(task, task_context, process)

    async def mic_check(self):
        await self.stream_handler.send_chunk("Mic Check")
        await self.stream_handler.send_chunk(f"Message: {str(self.mic_check_message)}")
        await self.stream_handler.send_chunk(
            f"Log Service Mic Check Response to: {self.mic_check_message} | One more response coming from Log Service.\n\n"
        )
        await self.stream_handler.send_end()

    def _ensure_log_dir(self):
        """Ensure the log directories exist"""
        try:
            os.makedirs(self.log_dir, exist_ok=True)
            # Ensure temp/logs directory for local logs
            os.makedirs(os.path.join(settings.TEMP_DIR, "logs"), exist_ok=True)
        except Exception as e:
            self.logger.error(f"Error creating log directories: {e}")
            raise

    def _get_actual_filename(self, friendly_name: str) -> str:
        """Map user-friendly log name to actual filename or full path"""
        filepath = LOG_FILE_MAPPING.get(friendly_name, "run_py.log")
        # For non-local logs, prepend log_dir; for local logs, use full path directly
        if friendly_name != "local logs":
            return os.path.join(self.log_dir, filepath)
        return filepath  # Already a full path for local logs

    async def read_logs(self):
        """Read logs based on self.filename, self.lines, and self.search"""
        filepath = self._get_actual_filename(self.filename)
        if not os.path.exists(filepath):
            await self.stream_handler.send_chunk(f"Error: Log file {self.filename} not found")
            await self.stream_handler.send_end()
            return

        try:
            with open(filepath, 'r') as f:
                log_lines = f.readlines()

                # Apply search filter if provided
                if self.search:
                    log_lines = [line for line in log_lines if re.search(self.search, line, re.IGNORECASE)]

                # Get last N lines or all
                result = log_lines[-self.lines:] if self.lines > 0 else log_lines

                # Stream logs as text
                for line in result:
                    await self.stream_handler.send_chunk(line)
                await self.stream_handler.send_end()

        except Exception as e:
            self.logger.error(f"Error reading log file {filepath}: {e}")
            await self.stream_handler.send_chunk(f"Error reading logs: {str(e)}")
            await self.stream_handler.send_end()

    async def tail_logs(self):
        """Continuously tail logs based on self.filename and self.interval"""
        # If already tailing, stop the existing task gracefully
        if self._tail_active:
            await self.stream_handler.send_chunk(
                f"Existing tailing task for {self.filename} detected, stopping it to start a new one")
            self._tail_active = False
            # Wait briefly to allow the existing task to clean up
            await asyncio.sleep(0.1)

        filepath = self._get_actual_filename(self.filename)
        if not os.path.exists(filepath):
            await self.stream_handler.send_chunk(f"Error: Log file {self.filename} not found")
            await self.stream_handler.send_end()
            return

        self._tail_active = True
        await self.stream_handler.send_chunk(f"Started tailing {self.filename}")
        last_size = 0

        try:
            while self._tail_active:
                try:
                    with open(filepath, 'r') as f:
                        f.seek(0, os.SEEK_END)
                        current_size = f.tell()

                        # Handle log rotation
                        if current_size < last_size:
                            await self.stream_handler.send_chunk(
                                f"Log rotation detected for {self.filename}, resetting position")
                            last_size = 0

                        if current_size > last_size:
                            f.seek(last_size)
                            new_lines = f.readlines()
                            for line in new_lines:
                                await self.stream_handler.send_chunk(line)
                            last_size = current_size

                except FileNotFoundError:
                    await self.stream_handler.send_chunk(
                        f"Error: Log file {self.filename} no longer exists, stopping tail")
                    self._tail_active = False
                    break
                except PermissionError:
                    await self.stream_handler.send_chunk(
                        f"Error: Permission denied accessing {self.filename}, stopping tail")
                    self._tail_active = False
                    break
                except Exception as e:
                    await self.stream_handler.send_chunk(f"Error tailing {self.filename}: {str(e)}")
                    self._tail_active = False
                    break

                await asyncio.sleep(self.interval)

        except Exception as e:
            await self.stream_handler.send_chunk(f"Unexpected error tailing {self.filename}: {str(e)}")
            self._tail_active = False

        finally:
            if self._tail_active:
                self._tail_active = False
            await self.stream_handler.send_chunk(f"Stopped tailing {self.filename}")
            await self.stream_handler.send_end()

    async def stop_tail_logs(self):
        """Stop the active log tailing task"""
        if not self._tail_active:
            await self.stream_handler.send_chunk("No active tailing task to stop")
            await self.stream_handler.send_end()
            return

        self._tail_active = False
        await self.stream_handler.send_chunk("Log tailing stopped")
        await self.stream_handler.send_end()

    async def get_log_files(self):
        """List available log files with user-friendly names"""
        try:
            files = []
            for friendly_name, filepath in LOG_FILE_MAPPING.items():
                actual_filepath = self._get_actual_filename(friendly_name)
                if os.path.isfile(actual_filepath):
                    stat = os.stat(actual_filepath)
                    files.append({
                        'name': friendly_name,  # Use friendly name
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
                else:
                    await self.stream_handler.send_chunk(
                        f"Warning: Log file {friendly_name} not found at {actual_filepath}")
            if files:
                await self.stream_handler.send_object(files)
            else:
                await self.stream_handler.send_chunk("No log files found")
            await self.stream_handler.send_end()
        except Exception as e:
            self.logger.error(f"Error listing log files: {e}")
            await self.stream_handler.send_chunk(f"Error listing log files: {str(e)}")
            await self.stream_handler.send_end()

    async def get_all_logs(self):
        """Read all logs from the specified file"""
        self.lines = 0  # Set to 0 to get all lines
        await self.read_logs()
