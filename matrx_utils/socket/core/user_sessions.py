import asyncio
import os
from datetime import datetime, timedelta

import jwt
from socketio import AsyncNamespace
from supabase import create_client, Client

# from automation_matrix.simple.conductor import Conductor
# from automation_matrix.simple.execution import get_single
from matrx_utils import vcprint
from matrx_utils.socket.core.app_factory import get_app_factory

supabase_url = os.environ.get("SUPABASE_MATRIX_URL")
supabase_key = os.environ.get("SUPABASE_MATRIX_KEY")
supabase_jwt_secret = os.environ.get("SUPABASE_MATRIX_JWT_SECRET")

# single = get_single()
# register = single.registry

verbose = True
debug = False
info = False

_user_session_namespace_instance = None


class UserSessionNamespace(AsyncNamespace):
    def __init__(self, namespace="/UserSession"):
        super().__init__(namespace)
        self.authenticated_users = {}
        self.user_session_data = {}
        self.service_instances = {}
        self.session_expiry = {}
        self.cleanup_tasks = {}
        # self.conductor = Conductor(single)
        # self.task_manager = self.conductor.task_manager
        self.supabase: Client = create_client(supabase_url, supabase_key)
        self.user_service_factories = {}  # New: Store ServiceFactory per user
        self._lock = asyncio.Lock()

    async def on_connect(self, sid, environ, auth):
        try:
            token = auth.get("token")

            # Special case for admin UUID
            if token == "75ba80cb-2508-4423-8fc1-4216a6b44212":
                decoded_token = {
                    "sub": "admin",
                    "email": "admin@system",
                    "user_metadata": {"full_name": "Admin"},
                }
            else:
                if not token:
                    raise ConnectionRefusedError("No authentication token provided")
                decoded_token = jwt.decode(
                    token,
                    supabase_jwt_secret,
                    algorithms=["HS256"],
                    options={"verify_aud": False},
                )

            # Extract user information from token claims
            user_id = decoded_token.get("sub")
            email = decoded_token.get("email")
            user_metadata = decoded_token.get("user_metadata", {})
            user_name = user_metadata.get("full_name") or user_metadata.get("name") or user_metadata.get("username")

            self.authenticated_users[sid] = user_id
            if user_id not in self.user_session_data:
                self.user_session_data[user_id] = {
                    "last_connected": datetime.now().isoformat(),
                    "active_sid": sid,
                    "connection_count": 1,
                    "email": email,
                    "user_name": user_name,
                }

            else:
                self.user_session_data[user_id].update(
                    {
                        "last_connected": datetime.now().isoformat(),
                        "active_sid": sid,
                        "connection_count": self.user_session_data[user_id].get("connection_count", 0) + 1,
                        "email": email,
                        "user_name": user_name,
                    }
                )

            self.session_expiry[sid] = datetime.now() + timedelta(minutes=30)
            await self.schedule_session_cleanup(sid)
            vcprint(
                verbose=True,
                data=f"[SOCKET USER SESSION] Connected SID: {sid} | User ID: {user_id} | User Name: {user_name or email}",
                color="blue",
            )

            # Create and register a ServiceFactory for this user
            if user_id not in self.user_service_factories:
                self.user_service_factories[user_id] = get_app_factory()
                vcprint(
                    verbose=True,
                    data=f"[SOCKET USER SESSION] New Service Factory Created for user: {user_id}",
                    color="green",
                )

            return True

        except jwt.InvalidTokenError as e:
            vcprint(
                verbose=True,
                data=f"[SOCKET USER SESSION] Invalid token error for SID {sid}: {str(e)}",
                color="red",
            )
            raise ConnectionRefusedError("Invalid authentication token")

    async def on_disconnect(self, sid):
        vcprint(
            verbose=True,
            data=f"[SOCKET USER SESSION] Client disconnected with session ID: {sid}",
            color="blue",
        )
        if sid in self.cleanup_tasks:
            self.cleanup_tasks[sid].cancel()

        # Store disconnect time
        if sid in self.authenticated_users:
            user_id = self.authenticated_users[sid]
            if user_id in self.user_session_data:
                self.user_session_data[user_id]["last_disconnect"] = datetime.now().isoformat()

    async def on_authenticate(self, sid, data):
        vcprint(
            verbose=verbose,
            pretty=True,
            data=data,
            title=f"[Socket UserSession authenticate] Request from {sid} with:",
            color="cyan",
        )
        matrix_id = await self.validate_user(data)
        if matrix_id:
            self.authenticated_users[sid] = matrix_id
            self.user_session_data[matrix_id] = self.user_session_data.get(matrix_id, {})
            self.session_expiry[sid] = datetime.now() + timedelta(minutes=30)
            return {
                "status": "success",
                "message": "User authenticated",
                "matrix_id": matrix_id,
            }
        else:
            return {"status": "error", "message": "User not authenticated"}

    async def on_reconnect(self, sid, data):
        vcprint(
            verbose=verbose,
            pretty=True,
            data=data,
            title=f"[Socket UserSession Reconnect] Request from {sid} with:",
            color="cyan",
        )

        matrix_id = data.get("matrix_id")
        if matrix_id in self.user_session_data:
            self.authenticated_users[sid] = matrix_id
            self.session_expiry[sid] = datetime.now() + timedelta(minutes=30)
            self.user_session_data[matrix_id]["last_connected"] = datetime.now().isoformat()
            self.user_session_data[matrix_id]["active_sid"] = sid
            return {
                "status": "success",
                "message": "Session reconnected",
                "matrix_id": matrix_id,
            }
        else:
            return {"status": "error", "message": "Session not found"}

    async def on_get_user_data(self, sid):
        vcprint(
            verbose=verbose,
            data=f"[Socket UserSession Get User Data] Request from {sid}",
            color="cyan",
        )

        if sid in self.authenticated_users:
            matrix_id = self.authenticated_users[sid]
            self.session_expiry[sid] = datetime.now() + timedelta(minutes=30)
            return {
                "status": "success",
                "matrix_id": matrix_id,
                "data": self.user_session_data[matrix_id],
            }
        else:
            return {"status": "error", "message": "User not authenticated"}

    async def on_update_user_data(self, sid, data):
        vcprint(
            verbose=verbose,
            pretty=True,
            data=data,
            title=f"[Socket UserSession Update User Data] Request from {sid} with:",
            color="cyan",
        )

        if sid in self.authenticated_users:
            user_id = self.authenticated_users[sid]
            self.user_session_data[user_id].update(data)
            self.session_expiry[sid] = datetime.now() + timedelta(minutes=30)
            return {"status": "success", "message": "User data updated"}
        else:
            return {"status": "error", "message": "User not authenticated"}

    async def validate_user(self, user):
        matrix_user_id = user.get("user_id")

        vcprint(
            verbose=verbose,
            data=user,
            title=f"[Socket UserSession Validate User] Request from Matrix ID {matrix_user_id} with:",
            color="cyan",
        )

        return matrix_user_id

    async def schedule_session_cleanup(self, sid):
        self.cleanup_tasks[sid] = asyncio.create_task(self.cleanup_session(sid))

    async def cleanup_session(self, sid):
        while True:
            await asyncio.sleep(60)
            if sid not in self.session_expiry:
                break

            current_time = datetime.now()
            if current_time > self.session_expiry[sid]:
                async with self._lock:
                    if sid in self.authenticated_users:
                        matrix_id = self.authenticated_users[sid]
                        user_data = self.user_session_data.get(matrix_id, {})

                        user_data["last_disconnect"] = current_time.isoformat()
                        start_time = datetime.fromisoformat(user_data.get("last_connected", current_time.isoformat()))
                        user_data["session_duration"] = str(current_time - start_time)

                        await self.save_instance_to_database(matrix_id, user_data)

                        del self.authenticated_users[sid]
                        del self.session_expiry[sid]

                        if matrix_id in self.service_instances:
                            del self.service_instances[matrix_id]
                            del self.user_service_factories[matrix_id]
                            vcprint(
                                verbose=True,
                                data=f"[SOCKET USER SESSION] Removed ServiceFactory for user: {matrix_id}",
                                color="red",
                            )

                        await self.disconnect(sid)
                        vcprint(
                            verbose=verbose,
                            data=f"[Socket UserSession Cleanup Session] Cleaning Up {sid}, Matrix ID: {matrix_id}",
                            color="red",
                        )
                break

    async def save_instance_to_database(self, matrix_id, data):
        try:
            storage_data = {
                "matrix_id": matrix_id,
                "last_connected": data.get("last_connected"),
                "last_disconnect": data.get("last_disconnect"),
                "session_duration": data.get("session_duration"),
                "connection_count": data.get("connection_count"),
                "active_sid": data.get("active_sid"),
                "session_data": data,
            }

            result = await self.supabase.table("user_sessions").upsert(storage_data).execute()

            vcprint(
                verbose=verbose,
                data=f"[Socket UserSession Database] Saved session data for {matrix_id}",
                color="green",
            )

            return result

        except Exception as e:
            vcprint(
                verbose=verbose,
                data=f"[Socket UserSession Database Error] Failed to save session for {matrix_id}: {str(e)}",
                color="red",
            )
            return None

    async def get_service_instance(self, service_class, event, sid, stream_handler=None):
        user_id = self.authenticated_users.get(sid)
        if not user_id:
            raise ValueError("User not authenticated")

        vcprint(
            verbose=True,
            data=f"[Socket.io Service] Getting service for user: {user_id}, event: {event}",
            color="blue",
        )

        if user_id not in self.service_instances:
            vcprint(
                verbose=True,
                data=f"[Socket.io Service] Creating new user instance map for {user_id}",
                color="blue",
            )
            self.service_instances[user_id] = {}

        if event not in self.service_instances[user_id]:
            vcprint(
                verbose=True,
                data=f"[Socket.io Service] Creating new service instance for event: {event}",
                color="blue",
            )
            self.service_instances[user_id][event] = service_class(stream_handler=stream_handler)
        else:
            if stream_handler is not None:
                vcprint(
                    verbose=True,
                    data=f"[Socket.io Service] Updating stream handler for event: {event}",
                    color="blue",
                )
                self.service_instances[user_id][event].stream_handler = stream_handler

        return self.service_instances[user_id][event]

    async def reset_service_instance(self, event, sid):
        user_id = self.authenticated_users.get(sid)
        if not user_id:
            raise ValueError("User not authenticated")

        vcprint(
            verbose=True,
            data=f"[Socket.io Service] Attempting to reset service for user: {user_id}, event: {event}",
            color="yellow",
        )

        if user_id not in self.service_instances:
            vcprint(
                verbose=True,
                data=f"[Socket.io Service] No services found for user: {user_id}",
                color="red",
            )
            return

        if event in self.service_instances[user_id]:
            vcprint(
                verbose=True,
                data=f"[Socket.io Service] Successfully reset service for event: {event}",
                color="green",
            )
            del self.service_instances[user_id][event]

    async def task_request(self, sid, data):
        vcprint(
            verbose=verbose,
            pretty=True,
            data=data,
            title=f"[Socket UserSession Task Request] Request from {sid} with:",
            color="cyan",
        )

        if sid in self.authenticated_users:
            matrix_id = self.authenticated_users[sid]
            self.session_expiry[sid] = datetime.now() + timedelta(minutes=30)

    def is_authenticated(self, sid):
        return sid in self.authenticated_users

    def get_user_id(self, sid):
        return self.authenticated_users.get(sid)

    def get_user_session_data(self, matrix_id):
        return self.user_session_data.get(matrix_id, {})

    async def get_user_factory_and_id(self, sid):
        """
        Retrieve the user's ServiceFactory and user_id given a session ID (sid).

        Args:
            sid (str): The session ID.

        Returns:
            tuple: (user_id, service_factory) if the sid is valid, else (None, None).
        """
        user_id = self.authenticated_users.get(sid)
        if not user_id:
            vcprint(
                verbose=True,
                data=f"[SOCKET USER SESSION] No user found for SID: {sid}",
                color="red",
            )
            return None, None

        service_factory = self.user_service_factories.get(user_id)
        if not service_factory:
            vcprint(
                verbose=True,
                data=f"[SOCKET USER SESSION] No ServiceFactory found for user: {user_id}",
                color="red",
            )
            return user_id, None

        vcprint(
            verbose=True,
            data=f"[SOCKET USER SESSION] Retrieved ServiceFactory for SID: {sid}, user: {user_id}",
            color="blue",
        )
        return user_id, service_factory


def get_user_session_namespace():
    global _user_session_namespace_instance
    if _user_session_namespace_instance is None:
        _user_session_namespace_instance = UserSessionNamespace("/UserSession")
        vcprint(
            "[SOCKET USER SESSION] User Session Namespace Initialized",
            verbose=True,
            color="green",
            inline=True,
        )
    return _user_session_namespace_instance
