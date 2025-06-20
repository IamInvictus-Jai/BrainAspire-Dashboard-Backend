from dependency_injector import containers, providers
from app.config.settings import get_settings
from app.core.logger import get_logger
from app.db.client import MongoDBClient
from app.core.security import Security

# Services
from app.services.auth_service import AuthService
from app.services.admin_services import AdminService
from app.services.payment_services import PaymentService

# Repositories
from app.repositories.auth_repository import AuthRepository
from app.repositories.base_repository import BaseRepository
from app.repositories.admin_repository import AdminRepository
from app.repositories.payment_repository import PaymentRepository


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
                "app.middlewares.globalExceptionHandlers",
            ],
        packages=[
            "app.api.v1",
        ]
    )

    # Singletons
    settings = providers.Singleton(get_settings)
    logger = providers.Singleton(get_logger, "BrainAspire", "app/logs")
    db = providers.Singleton(MongoDBClient, settings, logger)
    baseDB = providers.Singleton(BaseRepository, db)
    security = providers.Singleton(Security, settings, logger)

    # Repositories
    auth_repo = providers.Factory(AuthRepository, db)
    admin_repo = providers.Factory(AdminRepository, db)
    payment_repo = providers.Factory(PaymentRepository, db)

    # Services
    auth_service = providers.Factory(AuthService, security, auth_repo)
    admin_service = providers.Factory(AdminService, admin_repo, security, logger)
    payment_service = providers.Factory(PaymentService, payment_repo, logger)

    