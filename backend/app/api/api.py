from datetime import timedelta
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas.schemas import *
from app.repositories.user import UserRepository
from app.repositories.articles import ArticleRepository, get_article_by_id
from app.services.deps import get_db
from app.services.role_checker import require_role
from app.models.models import User

from app.core.auth import authenticate_user, create_access_token, get_current_user
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES
from app.core.security import get_password_hash


ROUTERS = []

def routers_fabric(prefix: str, tags: List[str] | None = None) -> APIRouter:
    new_router = APIRouter(prefix=prefix, tags=tags)
    ROUTERS.append(new_router)
    return new_router


user_router = routers_fabric(prefix="/users", tags=["Users"])

@user_router.get("/{username}", response_model=UserGet)
async def get_users_one(username: str, db_session: AsyncSession = Depends(get_db)):
    user = await UserRepository.get_one(db_session, username)
    if user is None:
        return HTTPException(404, "User not found")
    return user

@user_router.get("/", response_model=List[UserGet])
async def get_users_many(
    db_session: AsyncSession = Depends(get_db),
    offset: int = 0,
    limit: int = 10    
):
    users = await UserRepository.get_many(
        db_session,
        offset=offset,
        limit=limit
    )
    return users

@user_router.post("/create", response_model=UserGet)
async def create_user(data: UserCreate, db_session: AsyncSession = Depends(get_db)):
    new_user = await UserRepository.create(db_session, data.username, data.name, get_password_hash(data.password))
    return new_user

@user_router.put("/{username}", response_model=UserGet)
async def create_user(data: UserPut,
                      username: str,
                      current_user: Annotated[User, Depends(require_role(["admin"]))],
                      db_session: AsyncSession = Depends(get_db)):
    user = await UserRepository.update(db_session, username, data.model_dump())
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if current_user.username != user.username and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")
    return user

@user_router.delete("/{username}")
async def delete_user(
    username: str,
    current_user: AsyncSession = Depends(require_role(["admin"])),
    db_session: AsyncSession = Depends(get_db)
):
    return await UserRepository.delete(db_session, username)


general_router = routers_fabric(prefix="", tags=["General"])

@general_router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db_session: AsyncSession = Depends(get_db)
):
    user = await authenticate_user(db_session, form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta = access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

@general_router.get("/home", response_model=UserGet)
async def get_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user

@general_router.get("/liveness")
async def liveness():
    return {"status": "ok"}


article_router = routers_fabric(prefix="/articles", tags=["Articles"])

@article_router.get("/{article_id}", response_model=ArticleGet)
async def get_article(
    article_id: int,
    db_session: Annotated[AsyncSession, Depends(get_db)]
):
    article = await ArticleRepository.get_one(
        db=db_session,
        article_id=article_id
    )
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return article

@article_router.get("/", response_model=List[ArticleGet])
async def get_articles_list(
    db_session: AsyncSession = Depends(get_db),
    offset: int = 0,
    limit: int = 10
):
    articles = await ArticleRepository.get_all(
        db=db_session,
        offset=offset,
        limit=limit
    )
    return articles

@article_router.post("/create", response_model=ArticleGet)
async def create_article(
    article_data: ArticleCreate,
    db_session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    new_article = await ArticleRepository.create(
        db=db_session,
        author_id=current_user.id,
        title=article_data.title,
        text=article_data.text
    )
    return new_article

@article_router.put("/{article_id}", response_model=ArticleGet)
async def update_article(
    article_id: int,
    article_data: ArticleUpdate,
    db_session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    article = await get_article_by_id(db=db_session, article_id=article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    if article.author_id != current_user.id or current_user.role not in ["editor", "admin"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    updated_article = await ArticleRepository.update(
        db=db_session,
        article_id=article_id,
        article_data=article_data.model_dump()
    )
    return updated_article

@article_router.delete("/{article_id}")
async def delete_article(
    article_id: int,
    db_session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    article = await ArticleRepository.get_one(db=db_session, article_id=article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    if article.author_id != current_user.id or current_user.role not in ["admin"]:
        raise HTTPException(status_code=403, detail="forbidden")
    return await ArticleRepository.delete(db=db_session, article_id=article_id)


search_router = routers_fabric(prefix="/search", tags=["Search"])

@search_router.get("/article/{query}", response_model=List[ArticleGet])
async def searth_article(
    db_session: Annotated[AsyncSession, Depends(get_db)],
    query: str = "",
    offset: str = 0,
    limit: str = 10
):
    articles = await ArticleRepository.search(
        db=db_session,
        query=query,
        offset=offset,
        limit=limit
    )
    return articles

@search_router.get("/users/{query}", response_model=List[UserGet])
async def search_users(
    db_session: Annotated[AsyncSession, Depends(get_db)],
    query: str = "",
    offset: str = 0,
    limit: str = 10
):
    users = await UserRepository.search(
        db=db_session,
        query=query,
        offset=offset,
        limit=limit
    )
    return users