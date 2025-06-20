from typing import Annotated
from fastapi import Depends
from dependency_injector.wiring import Provide

from logging import Logger
from app.config.settings import Settings
from app.db.client import MongoDBClient

from app.core.security import Security
from app.dependencies.container import Container
from app.dependencies.jwtAuth import get_current_user_id


# Services
from app.services.auth_service import AuthService
from app.services.admin_services import AdminService
from app.services.payment_services import PaymentService


class Dependencies:
    """
    Central dependency management class that defines type-safe dependencies
    for dependency injection throughout the application.
    """
    LoggerDependency = Annotated[Logger, Depends(Provide[Container.logger])]
    SettingsDependency = Annotated[Settings, Depends(Provide[Container.settings])]
    MongoDBClientDependency = Annotated[MongoDBClient, Depends(Provide[Container.db])]
    SecurityDependency = Annotated[Security, Depends(Provide[Container.security])]
    AuthService = Annotated[AuthService, Depends(Provide[Container.auth_service])]
    JWTAuthDependency = Annotated[str, Depends(get_current_user_id)]
    AdminService = Annotated[AdminService, Depends(Provide[Container.admin_service])]
    PaymentService = Annotated[PaymentService, Depends(Provide[Container.payment_service])]
    