from typing import List

from pydantic import BaseModel, Field
from datetime import datetime


class ArticleCreate(BaseModel):
    title: str = Field(..., description="Title of the article", example="Nice Little Title")
    text: str = Field(..., description="Maintext ofthe article", example="Nice little text")

class ArticleGet(BaseModel):
    id: int
    title: str
    text: str
    author: UserShort
    created_at: datetime

class ArticleUpdate(BaseModel):
    title: str
    text: str


class UserShort(BaseModel):
    username: str
    name: str


class Token(BaseModel):
    __tablename__ = "token"

    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None


class UserCreate(BaseModel):
    username: str
    name: str
    password: str
    role: str = "user"

class UserGet(BaseModel):
    username: str
    id: int
    name: str
    role: str

    class Config:
        from_attributes = True

class UserWithArticles(BaseModel):
    username: str
    id: int
    name: str
    role: str
    articles: List[ArticleGet]

    class Config:
        from_attributes = True


class UserPut(BaseModel):
    name: str | None
    password: str | None
