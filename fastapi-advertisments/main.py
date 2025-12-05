# main.py
from fastapi import FastAPI, Depends, HTTPException, Query
from typing import Optional, List

from app import crud, schemas, models
from app.database import get_db, engine, Base
from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI(title="Advertisement Service")

# создание таблиц при старте
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.post("/advertisement", response_model=schemas.Advertisement, status_code=201)
async def create_advertisement(advertisement: schemas.AdvertisementCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_advertisement(db=db, advertisement=advertisement)

@app.get("/advertisement/{advertisement_id}", response_model=schemas.Advertisement)
async def read_advertisement(advertisement_id: int, db: AsyncSession = Depends(get_db)):
    db_advertisement = await crud.get_advertisement(db, advertisement_id=advertisement_id)
    if db_advertisement is None:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return db_advertisement

@app.patch("/advertisement/{advertisement_id}", response_model=schemas.Advertisement)
async def update_advertisement(advertisement_id: int, advertisement_update: schemas.AdvertisementUpdate,
                         db: AsyncSession = Depends(get_db)):
    db_advertisement = await crud.update_advertisement(db, advertisement_id=advertisement_id,
                                                  advertisement_update=advertisement_update)
    if db_advertisement is None:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return db_advertisement

@app.delete("/advertisement/{advertisement_id}")
async def delete_advertisement(advertisement_id: int, db: AsyncSession = Depends(get_db)):
    success = await crud.delete_advertisement(db, advertisement_id=advertisement_id)
    if not success:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return {"message": "Advertisement deleted successfully"}

@app.get("/advertisement", response_model=List[schemas.Advertisement])
async def search_advertisements(
    title: Optional[str] = Query(None, description="Поиск по заголовку"),
    description: Optional[str] = Query(None, description="Поиск по описанию"),
    price_min: Optional[float] = Query(None, description="Минимальная цена"),
    price_max: Optional[float] = Query(None, description="Максимальная цена"),
    author: Optional[str] = Query(None, description="Поиск по автору"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    return await crud.search_advertisements(
        db=db,
        title=title,
        description=description,
        price_min=price_min,
        price_max=price_max,
        author=author,
        limit=limit,
        offset=offset
    )

@app.get("/")
async def read_root():
    return {"message": "Advertisement Service API"}
