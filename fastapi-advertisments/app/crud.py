from sqlalchemy.orm import Session
from sqlalchemy import or_
from . import models, schemas


def create_advertisement(db: Session, advertisement: schemas.AdvertisementCreate):
    db_advertisement = models.Advertisement(**advertisement.model_dump())
    db.add(db_advertisement)
    db.commit()
    db.refresh(db_advertisement)
    return db_advertisement


def get_advertisement(db: Session, advertisement_id: int):
    return db.query(models.Advertisement).filter(models.Advertisement.id == advertisement_id).first()


def update_advertisement(db: Session, advertisement_id: int, advertisement_update: schemas.AdvertisementUpdate):
    db_advertisement = db.query(models.Advertisement).filter(models.Advertisement.id == advertisement_id).first()
    if db_advertisement:
        update_data = advertisement_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_advertisement, field, value)
        db.commit()
        db.refresh(db_advertisement)
    return db_advertisement


def delete_advertisement(db: Session, advertisement_id: int):
    db_advertisement = db.query(models.Advertisement).filter(models.Advertisement.id == advertisement_id).first()
    if db_advertisement:
        db.delete(db_advertisement)
        db.commit()
        return True
    return False


def search_advertisements(db: Session, title: str = None, description: str = None,
                          price_min: float = None, price_max: float = None,
                          author: str = None):
    query = db.query(models.Advertisement)

    if title:
        query = query.filter(models.Advertisement.title.contains(title))
    if description:
        query = query.filter(models.Advertisement.description.contains(description))
    if price_min is not None:
        query = query.filter(models.Advertisement.price >= price_min)
    if price_max is not None:
        query = query.filter(models.Advertisement.price <= price_max)
    if author:
        query = query.filter(models.Advertisement.author.contains(author))

    return query.order_by(models.Advertisement.created_at.desc()).all()