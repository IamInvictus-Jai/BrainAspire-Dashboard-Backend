from fastapi import HTTPException, status, Depends
from dependency_injector.wiring import Provide, inject
from app.dependencies.container import Container
from fastapi.security import OAuth2PasswordBearer
from app.core.security import Security
from app.exceptions.authExceptions import TokenExpired, InvalidCredentials

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/login")

@inject
async def get_current_user_id(
    token: str = Depends(oauth2_scheme),
    security: Security = Depends(Provide[Container.security])) -> str:
    try:
        return security.decode_token(token)
    except TokenExpired:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired. Please log in again.",
        )
    except InvalidCredentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials.",
        )
