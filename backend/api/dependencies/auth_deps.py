"""Dépendances FastAPI d'authentification et d'extraction de l'utilisateur courant."""

from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from jwt.exceptions import InvalidTokenError

from auth.authenticate_tools import decode_access_token
from core.logging import logger
from core.security import oauth2_scheme
from models.token import TokenData
from models.user import User, UserInDB

from .user_loader import get_user


async def get_token_header(x_token: Annotated[str, Header()]) -> None:
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")


async def get_query_token(token: str) -> None:
    if token != "jessica":
        raise HTTPException(status_code=400, detail="No Jessica token provided")


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> UserInDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        user_login = payload.get("login")
        if user_login is None:
            logger.error(f"Login error with payload: {payload}")
            raise credentials_exception
        token_data = TokenData(login=user_login)
    except InvalidTokenError as e:
        logger.error(f"Invalid token : {e}")
        raise credentials_exception from e
    user = get_user(token_data.login)
    if user is None:
        logger.error(f"Login error with payload: {payload}")
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    return current_user
