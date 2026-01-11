import uuid
from sqlalchemy import Column, String, DateTime,ForeignKey,Boolean
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.config.db import Base

class User(Base):
    __tablename__ = "users"

    id:int = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email:str = Column(String, unique=True, nullable=False)
    name:str = Column(String)
    google_id:str = Column(String, unique=True, nullable=False)
    avatar_url:str = Column(String)
    created_at:datetime = Column(DateTime(timezone=True), server_default=func.now())

class Refresh_Token(Base):
    __tablename__ = "refresh_token"

    id:uuid.UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id:uuid.UUID = Column(UUID(as_uuid=True), ForeignKey("users.id"),nullable=False)
    jti = Column(String, unique=True, nullable=False)
    revoked: bool = Column(Boolean,default=False)
    expires_at:datetime = Column(DateTime(timezone=True), nullable=False)
    created_at:datetime = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")