from typing import Annotated

from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
import jwt
from app.core.security import verify_password
from app.services.deps import get_db
from .config import ALGORITHM, SECRET
from fastapi import Depends, HTTPException
from app.schemas.schemas import TokenData
from app.repositories.user import get_user_by_username
from app.core.security import oauth2_scheme


async def authenticate_user(db, username, password):
    user = await get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

def create_access_token(data, expires_delta):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)],
                            db_session: AsyncSession = Depends(get_db)):
    credencials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise credencials_exception
        token_data = TokenData(username=username)
    except jwt.InvalidTokenError:
        raise credencials_exception
    user = await get_user_by_username(db_session, username=token_data.username)
    if user is None:
        raise credencials_exception
    return user
