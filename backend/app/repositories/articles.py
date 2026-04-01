from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from app.models.models import Article, User
from .user import get_user_by_id

from fastapi import HTTPException


class ArticleRepository:
    @staticmethod
    async def get_one(db: AsyncSession, article_id):
        article = await get_article_by_id(db, article_id)
        return article
    
    @staticmethod
    async def get_all(
        db: AsyncSession,
        offset: int,
        limit: int
    ):
        result = await db.execute(
            select(Article).offset(offset).limit(limit).options(selectinload(Article.author))
        )
        return result.scalars().all()
    
    @staticmethod
    async def create(db: AsyncSession, author_id:int, title, text):
        author = await get_user_by_id(db, author_id)
        if author is None:
            return HTTPException(status_code=404, detail="User not found")
        article = Article(
            title = title,
            text = text,
            author_id = author_id,
            author = author
        )
        db.add(article)
        await db.commit()
        await db.refresh(article)
        return article
    
    @staticmethod
    async def update(db: AsyncSession, article_id, article_data: dict):
        article = await get_article_by_id(db, article_id)
        if not article:
            return None
        for field, value in article_data.items():
            if not hasattr(Article, field):
                continue
            await db.execute (
                update(Article).where(Article.id == article_id).values({field: value})
            )
        await db.commit()
        await db.refresh(article)
        return article
    
    @staticmethod
    async def delete(db: AsyncSession, article_id):
        article = await get_article_by_id(db, article_id)
        if article is None:
            raise HTTPException(status_code=404, detail="Not found")
        await db.delete(article)
        await db.commit()
        return True
    
    @staticmethod
    async def search(db: AsyncSession, query, offset, limit):
        articles = await db.execute(
            select(Article).where(
                Article.text.ilike(f"%{query}%")
            ).options(
                selectinload(Article.author)
            ).offset(offset).limit(limit)
        )
        return articles.scalars().all()


async def get_article_by_id(db: AsyncSession, article_id):
    result = await db.execute(
        select(Article).options(selectinload(Article.author)).where(Article.id == article_id)
    )
    if result is None:
        return None
    return result.scalar_one_or_none()
