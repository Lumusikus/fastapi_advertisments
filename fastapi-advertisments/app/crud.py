# app/crud.py
from typing import List, Optional
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from . import models, schemas

async def create_advertisement(db: AsyncSession, advertisement: schemas.AdvertisementCreate):
    db_item = models.Advertisement(**advertisement.model_dump())
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
    author: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> List[models.Advertisement]:
    stmt = select(models.Advertisement)

    if title:
        stmt = stmt.where(models.Advertisement.title.ilike(f"%{title}%"))
    if description:
        stmt = stmt.where(models.Advertisement.description.ilike(f"%{description}%"))
    if price_min is not None:
        stmt = stmt.where(models.Advertisement.price >= price_min)
    if price_max is not None:
        stmt = stmt.where(models.Advertisement.price <= price_max)
    if author:
        stmt = stmt.where(models.Advertisement.author.ilike(f"%{author}%"))

    stmt = stmt.order_by(models.Advertisement.created_at.desc()).limit(limit).offset(offset)

    result = await db.execute(stmt)
    return result.scalars().all()
