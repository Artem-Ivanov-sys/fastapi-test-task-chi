from asyncio import run as arun

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.db.db import get_sessionmaker
from app.repositories.user import UserRepository
from app.repositories.articles import ArticleRepository


USERS_DATA = [
    {
        "username": "user1",
        "name": "Test",
        "hashed_password": get_password_hash("password1")
    },
    {
        "username": "editor1",
        "name": "Test",
        "hashed_password": get_password_hash("password2"),
        "role": "editor"
    },
    {
        "username": "admin1",
        "name": "Test",
        "hashed_password": get_password_hash("password3"),
        "role": "admin"
    }
]

ARTICLES_DATA = [
    {
        "author_id": 1,
        "title": "Article 1",
        "text": "Gnawing on the Bishops, crawling way up their system"
    },
    {
        "author_id": 1,
        "title": "Article 2",
        "text": "I look back in time through a telescope"
    },
    {
        "author_id": 2,
        "title": "Article 3",
        "text": "I've been catching my reflection already looking"
    },
    {
        "author_id": 2,
        "title": "Article 4",
        "text": "They keep me company, robots and machines in my room"
    },
    {
        "author_id": 3,
        "title": "Article 5",
        "text": "They say 'stay in your lane, boy', but we go where we want to"
    },
    {
        "author_id": 1,
        "title": "Article 6",
        "text": "I wish I found some better sounds noone's ever heard"
    },
]

async def add_users(session: AsyncSession):
    for user in USERS_DATA:
        await UserRepository.create(
            db = session,
            **user
        )

async def add_articles(session: AsyncSession):
    for article in ARTICLES_DATA:
        await ArticleRepository.create(
            db=session,
            **article
        )

async def fill_test_data():
    async with get_sessionmaker()() as session:
        await add_users(session)
        await add_articles(session)

if __name__ == "__main__":
    arun(fill_test_data())