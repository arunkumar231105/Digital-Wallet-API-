from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator


def validate_bcrypt_password_length(value: str) -> str:
    if len(value.encode("utf-8")) > 72:
        raise ValueError("Password cannot be longer than 72 bytes")
    return value


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=1, max_length=72)

    _password_bytes_validator = field_validator("password")(validate_bcrypt_password_length)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=72)

    _password_bytes_validator = field_validator("password")(validate_bcrypt_password_length)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class WalletResponse(BaseModel):
    id: int
    user_id: int
    balance: Decimal

    class Config:
        from_attributes = True


class AmountRequest(BaseModel):
    amount: Decimal


class TransferRequest(BaseModel):
    email: EmailStr
    amount: Decimal


class BalanceResponse(BaseModel):
    balance: Decimal


class TransactionResponse(BaseModel):
    id: int
    wallet_id: int
    type: Literal["deposit", "withdraw", "transfer_in", "transfer_out"]
    amount: Decimal
    timestamp: datetime
    counterparty_name: str | None = None

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    message: str


class AdminDepositRequest(BaseModel):
    email: EmailStr
    amount: Decimal


class UserStatusRequest(BaseModel):
    email: EmailStr


class FreezeUserRequest(BaseModel):
    user_email: EmailStr


class UserListResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    is_active: bool
    is_admin: bool
    is_frozen: bool

    class Config:
        from_attributes = True
