from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from time import time
from pymongo.errors import ServerSelectionTimeoutError
from pydantic import ValidationError

# DI dependencies
from dependency_injector.wiring import inject
from app.utils.dependencyManager import Dependencies


class ExceptionMiddleware(BaseHTTPMiddleware):

    @inject
    def __init__(self, app, logger:Dependencies.LoggerDependency):
        super().__init__(app)
        self.logger = logger

    async def dispatch(self, request: Request, call_next):
        start = time()
        self.logger.info(f"Incoming request: {request.method} {request.url}")
        try:
            response = await call_next(request)
        
        except ValidationError as e:
            # Pydantic validation errors
            self.logger.error(f"Validation Error: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={"detail": str(e)}
            )
        
        except ServerSelectionTimeoutError as e:
            self.logger.error(f"Database connection error: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={
                    "detail": "Database connection failed",
                    "message": "Unable to connect to database server"
                }
            )
        
        except Exception as e:
            self.logger.exception("Unhandled exception during request")
            raise
            # return JSONResponse(
            #     status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            #     content={
            #         "detail": "Something went wrong. Please try again later.",
            #         "message": str(e)
            #     }
            # )
        
        duration = round(time() - start, 2)
        self.logger.info(f"Request completed in {duration}s with status {response.status_code}")
        return response