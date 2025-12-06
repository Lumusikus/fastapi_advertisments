from typing import List, Optional
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from . import models, schemas

async def create_advertisement(db: AsyncSession, advertisement: schemas.AdvertisementCreate, user_id: int):
    db_item = models.Advertisement(
        title=advertisement.title,
        description=advertisement.description,
        price=advertisement.price,
        author_id=user_id
    )
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item



async def get_advertisement(db: AsyncSession, advertisement_id: int):
    result = await db.execute(select(models.Advertisement).where(models.Advertisement.id == advertisement_id))
    return result.scalar_one_or_none()

async def update_advertisement(db: AsyncSession, advertisement_id: int, advertisement_update: schemas.AdvertisementUpdate):
    result = await db.execute(select(models.Advertisement).where(models.Advertisement.id == advertisement_id))
    db_item = result.scalar_one_or_none()

    if not db_item:
        return None

    update_data = advertisement_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_item, field, value)

    await db.commit()
    await db.refresh(db_item)
    return db_item


async def delete_advertisement(db: AsyncSession, advertisement_id: int) -> bool:
    result = await db.execute(select(models.Advertisement).where(models.Advertisement.id == advertisement_id))
    db_item = result.scalar_one_or_none()
    if not db_item:
        return False
    await db.delete(db_item)
    await db.commit()
    return True

async def search_advertisements(
    db: AsyncSession,
    title: Optional[str] = None,
    description: Optional[str] = None,
    price_min: Optional[float] = None,
    price_max: Optional[float] = None,
    username_author: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
):
    stmt = select(models.Advertisement).join(models.User)

    if title:
        stmt = stmt.where(models.Advertisement.title.ilike(f"%{title}%"))
    if description:
        stmt = stmt.where(models.Advertisement.description.ilike(f"%{description}%"))
    if price_min is not None:
        stmt = stmt.where(models.Advertisement.price >= price_min)
    if price_max is not None:
        stmt = stmt.where(models.Advertisement.price <= price_max)
    if username_author:
        stmt = stmt.where(models.User.username.ilike(f"%{username_author}%"))

    stmt = stmt.order_by(models.Advertisement.created_at.desc()).limit(limit).offset(offset)

    result = await db.execute(stmt)
    return result.scalars().all()



from fastapi import HTTPException, status
from .auth import hash_password, verify_password, create_access_token


async def create_user(db: AsyncSession, user: schemas.UserCreate):
    result = await db.execute(select(models.User).where(models.User.username == user.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already exists")

    db_user = models.User(
        username=user.username,
        hashed_password=hash_password(user.password),
        role=user.role
    )

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def get_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    return result.scalar_one_or_none()

async def update_user(db: AsyncSession, user_id: int, payload: schemas.UserUpdate):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        return None
    if payload.username:
        user.username = payload.username
    if payload.password:
        user.hashed_password = hash_password(payload.password)
    if payload.role:
        user.role = payload.role
    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        return False
    await db.delete(user)
    await db.commit()
    return True


async def authenticate_user(db: AsyncSession, username: str, password: str):
    result = await db.execute(select(models.User).where(models.User.username == username))
    user = result.scalar_one_or_none()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None

    return user
