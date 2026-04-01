from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.core.security import get_password_hash
from app.models.models import User


class UserRepository:
    @staticmethod
    async def get_one(db: AsyncSession, username):
        user = await get_user_by_username(db, username)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    
    @staticmethod
    async def get_many(
        db: AsyncSession,
        offset: int,
        limit: int
    ):
        result = await db.execute(
            select(User).offset(offset).limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def create(db: AsyncSession, username, name, hashed_password, role="user"):
        user = User(username=username, name=name, hashed_password=hashed_password, role=role)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def delete(db: AsyncSession, username):
        user = await get_user_by_username(db, username)
        if user is None:
            raise HTTPException(status_code=404, detail="Not found")
        await db.delete(user)
        await db.commit()
        return True

    @staticmethod
    async def update(db: AsyncSession, username, user_data: dict):
        user = await get_user_by_username(db, username)
        if user is None:
            return None
        for field, value in user_data.items():
            print({field: value})
            if not hasattr(User, field):
                continue
            if field == "password":
                await db.execute (
                    update(User).where(User.username==username).values({"hashed_password": get_password_hash(value)})
                )
            else:
                await db.execute (
                    update(User).where(User.username==username).values({field: value})
                )
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def search(db: AsyncSession, query, offset, limit):
        users = await db.execute(
            select(User).where(
                User.username.ilike(f"%{query}%")
            ).offset(offset).limit(limit)
        )
        return users.scalars().all()

async def get_user_by_id(db: AsyncSession, user_id):
    result = await db.execute(
        select(User).where(User.id==user_id)
    )
    if result is None:
        return None
    return result.scalar_one_or_none()

async def get_user_by_username(db: AsyncSession, username):
    result = await db.execute(
        select(User).where(User.username==username)
    )
    if result is None:
        return None
    return result.scalar_one_or_none()