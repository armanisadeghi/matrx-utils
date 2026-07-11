"""Optional FastAPI router factories for matrx-utils file handling.

Hosts that want the canonical endpoint surface "for free" can mount
these factories instead of writing their own routers. Each factory
takes a configured ``FileService`` and returns an ``APIRouter``.

    from fastapi import FastAPI
    from matrx_utils.file_handling import FileService
    from matrx_utils.file_handling.fastapi import (
        build_file_router,
        build_asset_router,
        build_share_router,
    )

    file_service = FileService.from_env()
    app = FastAPI()
    app.include_router(build_file_router(file_service))
    app.include_router(build_asset_router(file_service))
    app.include_router(build_share_router(file_service))

The factories are intentionally minimal — they ship the core CRUD +
URL endpoints every host needs. Auth dependencies are caller-supplied
via the ``user_id_dep`` parameter (a FastAPI ``Depends(...)`` that
returns the authenticated user_id). This lets each host plug in its
own JWT validation, guest fingerprint flow, etc.

For more elaborate setups (presigned uploads, TUS resumable transport,
bulk operations, group ACL, search/trash), hosts can either:
  * subclass / extend these factories
  * write their own thin routers calling ``file_service.*`` methods
  * mount ``build_file_router`` AND a host-specific router side-by-side
"""

from .router_files import build_file_router
from .router_assets import build_asset_router
from .router_share import build_share_router

__all__ = [
    "build_file_router",
    "build_asset_router",
    "build_share_router",
]
