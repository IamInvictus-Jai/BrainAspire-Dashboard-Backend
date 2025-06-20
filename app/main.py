from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from contextlib import asynccontextmanager

from .config.settings import get_settings
from .middlewares.globalExceptionHandlers import ExceptionMiddleware
from .utils.routes import add_routes
from .dependencies.container import Container


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     """Lifespan handler replacing on_event('startup') and on_event('shutdown')"""
#     container = Container()

#     # Store container reference in app
#     app.container = container

#     try:
#         container.init_resources()
#         container.wire(
#             modules=[
#                 "app.middlewares.globalExceptionHandlers",
#             ],
#             packages=[
#                 "app.api.v1",
#             ]
#         )
#         container.logger().info("Container wired and resources initialized")
#     except Exception as e:
#         print(f"Startup failed: {str(e)}")
#         raise RuntimeError(f"Failed to initialize: {str(e)}")

#     yield  # App is now running

#     # Optional: Add shutdown logic here
#     # container.logger().info("Shutting down app...")

def init_resources(app: FastAPI):
    container = Container()
    
    # Store container reference in app
    app.container = container

    try:
        container.logger().info("Container wired and resources initialized")
        container.baseDB().connect()
        # container.baseDB().create_indexes()   # uncomment to create indexes
        container.wire(
            modules=[
                "app.middlewares.globalExceptionHandlers",
            ],
            packages=[
                "app.api.v1",
            ]
        )
        container.logger().info("Container wired and resources initialized\n\n")
    except Exception as e:
        container.logger().error(f"Startup failed: {str(e)}")
        raise RuntimeError(f"Failed to initialize: {str(e)}")

def create_app() -> FastAPI:
    settings = get_settings()

    # Create FastAPI instance
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION
    )

    # Add startup and shutdown events
    init_resources(app)

    # Set up CORS and exception middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=settings.allowed_methods,
        allow_headers=settings.allowed_headers,
    )
    app.add_middleware(ExceptionMiddleware)
    
    # Add Routers
    add_routes(app)

    return app

app = create_app()