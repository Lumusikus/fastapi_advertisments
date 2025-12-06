from fastapi import FastAPI, Depends, HTTPException, Query
from typing import Optional, List

from app import crud, schemas, models
from app.database import get_db, engine, Base
from app.auth import create_access_token
from sqlalchemy.ext.asyncio import AsyncSession
from app.deps import get_current_user

app = FastAPI(title="Advertisement Service")

# создание таблиц при старте
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.post("/advertisement", response_model=schemas.Advertisement, status_code=201)
async def create_advertisement(
    advertisement: schemas.AdvertisementCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return await crud.create_advertisement(db=db, advertisement=advertisement, user_id=current_user.id)

@app.get("/advertisement/{advertisement_id}", response_model=schemas.Advertisement)
async def read_advertisement(advertisement_id: int, db: AsyncSession = Depends(get_db)):
    db_advertisement = await crud.get_advertisement(db, advertisement_id=advertisement_id)
    if db_advertisement is None:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return db_advertisement

@app.patch("/advertisement/{advertisement_id}", response_model=schemas.Advertisement)
async def update_advertisement(
    advertisement_id: int,
    advertisement_update: schemas.AdvertisementUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_item = await crud.get_advertisement(db, advertisement_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    if current_user.role != "admin" and db_item.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Обновлять можно только свои объявления")

    updated = await crud.update_advertisement(db, advertisement_id, advertisement_update)
    return updated


@app.delete("/advertisement/{advertisement_id}")
async def delete_advertisement(
    advertisement_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_item = await crud.get_advertisement(db, advertisement_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    if current_user.role != "admin" and db_item.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Удалять можно только свои объявления")
    success = await crud.delete_advertisement(db, advertisement_id)
    return {"message": "Объявление успешно удалено"}

@app.get("/advertisement", response_model=List[schemas.Advertisement])
async def search_advertisements(
    title: Optional[str] = Query(None, description="Поиск по заголовку"),
    description: Optional[str] = Query(None, description="Поиск по описанию"),
    price_min: Optional[float] = Query(None, description="Минимальная цена"),
    price_max: Optional[float] = Query(None, description="Максимальная цена"),
    username_author: Optional[str] = Query(None, description="Поиск по автору"),
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
        username_author=username_author,
        limit=limit,
        offset=offset
    )

@app.get("/")
async def read_root():
    return {"message": "Advertisement Service API"}


@app.post("/login")
async def login(payload: schemas.UserLogin, db: AsyncSession = Depends(get_db)):
    user = await crud.authenticate_user(db, payload.username, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_access_token({"sub": user.username, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}


@app.post("/user", response_model=schemas.User, status_code=201)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_user(db, user)

@app.get("/user/{user_id}", response_model=schemas.User)
async def read_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.patch("/user/{user_id}", response_model=schemas.User)
async def update_user(
    user_id: int,
    payload: schemas.UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    if current_user is None:
        raise HTTPException(status_code=401, detail="Требуется войти в систему")
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    user = await crud.update_user(db, user_id, payload)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user

@app.delete("/user/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # обычный пользователь может удалять только себя
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    success = await crud.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return {"message": "User deleted"}


