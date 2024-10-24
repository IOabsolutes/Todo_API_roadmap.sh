from pydantic import EmailStr
from sqlmodel import SQLModel, Field, Column, String, Relationship


class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str = Field(sa_column=Column(String, nullable=False))
    email: EmailStr = Field(sa_column=Column(String, index=True, unique=True))
    password_hash: str = Field(sa_column=Column(String, nullable=False))

    tasks: list["Task"] = Relationship(back_populates="user")
