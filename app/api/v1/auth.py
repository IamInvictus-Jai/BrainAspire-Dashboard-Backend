from fastapi import APIRouter, HTTPException, Depends, status
from dependency_injector.wiring import inject
from app.utils.dependencyManager import Dependencies

from app.schemas.auth_schema import LoginRequest, Token
from app.dependencies.jwtAuth import get_current_user_id
from app.exceptions.authExceptions import UserNotFound, InvalidCredentials, AccessDenied

auth_router = APIRouter(
    prefix="/v1/auth",
    tags=["Authentication"],
    responses={404: {"description": "Not found"}},
    # dependencies=[Depends(get_current_user_id)],
)


@auth_router.post("/login", response_model=Token)
@inject
async def login(creds:LoginRequest, auth_service:Dependencies.AuthService):
    """
    Generates a JWT token given a valid user_id and password.

    Args:
        creds (LoginRequest): A Pydantic model containing the user_id and password.

    Returns:
        Token: A Pydantic model containing the JWT token.

    Raises:
        HTTPException: If the user_id is invalid (404) or the password is incorrect (401).
    """
    
    try:
        token = auth_service.authenticate(creds.user_id, creds.password)
        return Token(access_token=token)
    except UserNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AccessDenied as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except InvalidCredentials as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    
@auth_router.get("/token/validate")
async def validate_token(user_id: str = Depends(get_current_user_id)):
    """
    Validates a JWT token and retrieves the associated user ID.

    Args:
        user_id (str): The user ID extracted from the JWT token.

    Returns:
        dict: A dictionary containing the user ID.

    Raises:
        HTTPException: If the token is invalid or expired.
    """

    return {"user_id": user_id}