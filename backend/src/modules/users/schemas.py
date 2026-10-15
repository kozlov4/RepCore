import re
from typing import Self

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
    repeat_new_password: str

    @model_validator(mode="after")
    def check_passwords_match(self) -> Self:
        if self.new_password != self.repeat_new_password:
            raise ValueError("Паролі не співпадають")
        return self


class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    user_id: int
    email: EmailStr
    name: str
    surname: str
    phone: str

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)


class UserRegistration(BaseModel):
    name: str = Field(min_length=2, max_length=33, strip_whitespace=True)
    surname: str = Field(min_length=2, max_length=33, strip_whitespace=True)

    phone: str = Field(pattern=r"^\+?[1-9][0-9]{7,14}$")
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)

    @field_validator("email", mode="before")
    @classmethod
    def lowercase_email(cls, v: str) -> str:
        if isinstance(v, str):
            return v.lower().strip()
        return v

    @field_validator("password")
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Пароль має містити хоча б одну велику літеру")
        if not re.search(r"[a-z]", v):
            raise ValueError("Пароль має містити хоча б одну маленьку літеру")
        if not re.search(r"[0-9]", v):
            raise ValueError("Пароль має містити хоча б одну цифру")
        return v


class VerifyEmailRequest(BaseModel):
    email: EmailStr
    code: str = Field(
        min_length=6,
        max_length=6,
        pattern=r"^\d{6}$",
        description="6-значний цифровий код підтвердження",
    )


class MessageResponse(BaseModel):
    message: str
