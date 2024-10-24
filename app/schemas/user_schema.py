from fastapi import HTTPException, status
from pydantic import field_validator
from pydantic import BaseModel, EmailStr, Field
import re


class IUser(BaseModel):
    name: str = Field(min_length=3, max_length=20)
    email: EmailStr
    password: str = Field(min_length=8, max_length=20)


class IUserCreate(IUser):

    @field_validator('password', mode='after')
    def validate_password(cls, value, values):
        """Validate the password."""
        return cls.password_validator(value)

    @staticmethod
    def check_starts_with_capital(password):
        """Check if the password starts with a capital letter."""
        if not password[0].isupper():
            raise HTTPException(detail='Password must start with a capital letter',
                                status_code=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def check_at_least_two_digits(password):
        """Check if the password contains at least two digits."""
        digits = re.findall(r'\d', password)
        if len(digits) < 2:
            raise HTTPException(detail='Password must contain at least 2 digits',
                                status_code=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def check_at_least_one_special_char(password):
        """Check if the password contains at least one special character from the specified set."""
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\'":\\|,.<>/?]', password):
            raise HTTPException(detail='Password must contain at least 1 special symbol from the specified set',
                                status_code=status.HTTP_400_BAD_REQUEST)

    @classmethod
    def password_validator(cls, password):
        """Main password validator that calls individual checks."""
        cls.check_starts_with_capital(password)
        cls.check_at_least_two_digits(password)
        cls.check_at_least_one_special_char(password)
        return password

    class Config:
        from_attributes = True


class IUserUpdate(IUser):
    pass


class IUserRead(BaseModel):
    id: int
    name: str
    email: EmailStr
