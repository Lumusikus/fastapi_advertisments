from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app import crud, schemas, models
from app.database import engine, get_db

# cоздаем таблицы
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Advertisement Service")

@app.post("/advertisement", response_model=schemas.Advertisement, status_code=201)
def create_advertisement(advertisement: schemas.AdvertisementCreate, db: Session = Depends(get_db)):
    """
    Создание нового объявления
    """
    return crud.create_advertisement(db=db, advertisement=advertisement)

@app.get("/advertisement/{advertisement_id}", response_model=schemas.Advertisement)
def read_advertisement(advertisement_id: int, db: Session = Depends(get_db)):
    """
    Получение объявления по ID
    """
    db_advertisement = crud.get_advertisement(db, advertisement_id=advertisement_id)
    if db_advertisement is None:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return db_advertisement

@app.patch("/advertisement/{advertisement_id}", response_model=schemas.Advertisement)
def update_advertisement(advertisement_id: int, advertisement_update: schemas.AdvertisementUpdate,
                         db: Session = Depends(get_db)):
    """
    Обновление объявления по ID
    """
    db_advertisement = crud.update_advertisement(db, advertisement_id=advertisement_id,
                                                  advertisement_update=advertisement_update)
    if db_advertisement is None:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return db_advertisement

@app.delete("/advertisement/{advertisement_id}")
def delete_advertisement(advertisement_id: int, db: Session = Depends(get_db)):
    """
    Удаление объявления по ID
    """
    success = crud.delete_advertisement(db, advertisement_id=advertisement_id)
    if not success:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return {"message": "Advertisement deleted successfully"}

@app.get("/advertisement", response_model=List[schemas.Advertisement])
def search_advertisements(
    title: Optional[str] = Query(None, description="Поиск по заголовку"),
    description: Optional[str] = Query(None, description="Поиск по описанию"),
    price_min: Optional[float] = Query(None, description="Минимальная цена"),
    price_max: Optional[float] = Query(None, description="Максимальная цена"),
    author: Optional[str] = Query(None, description="Поиск по автору"),
    db: Session = Depends(get_db)
):
    """
    Поиск объявлений по различным параметрам
    """
    return crud.search_advertisements(
        db=db,
        title=title,
        description=description,
        price_min=price_min,
        price_max=price_max,
        author=author
    )

@app.get("/")
def read_root():
    return {"message": "Advertisement Service API"}