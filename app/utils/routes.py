from fastapi import FastAPI

# Routers
from app.api.health.server import server_health_router
from app.api.v1 import auth, admin, fee


def add_routes(app: FastAPI):
    """
    Adds routes to the FastAPI application instance.

    This function includes various routers to the FastAPI application,
    allowing it to handle specific routes defined in the imported router modules.

    Args:
        app (FastAPI): The FastAPI application instance to which the routes will be added.
    """

    app.include_router(server_health_router)
    app.include_router(auth.auth_router)
    app.include_router(admin.admin_router)
    app.include_router(fee.fee_router)