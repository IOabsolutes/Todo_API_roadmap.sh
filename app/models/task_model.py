from datetime import datetime, timezone
from sqlalchemy import Column, Text, String, DateTime, Integer
from sqlmodel import SQLModel, Field, Relationship
from .user_model import User


class Task(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(Integer, foreign_key="user.id")
    title: str = Field(String, nullable=False)
    description: str = Field(default=None, sa_column=Column(Text, nullable=True))
    create_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc),
                                sa_column=Column(DateTime(timezone=True), nullable=False))

    user: User = Relationship(back_populates="tasks")
