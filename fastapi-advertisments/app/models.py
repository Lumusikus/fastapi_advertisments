from sqlalchemy import Column, Integer, String, Float, DateTime, Index, ForeignKey
from sqlalchemy.sql import func
from .database import Base
from sqlalchemy.orm import relationship

class Advertisement(Base):
    __tablename__ = "advertisements"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    description = Column(String)
    price = Column(Float, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    author = relationship("User", backref="advertisements")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_title_description", "title", "description"),
    )

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="user")  # user | admin
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    ads = relationship("Advertisement", back_populates="author", cascade="all, delete-orphan")