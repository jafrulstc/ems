import uuid

from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    user_type: str
    branch_id: uuid.UUID | None = None
    role_id: uuid.UUID | None = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = None
    user_type: str | None = None
    branch_id: uuid.UUID | None = None
    role_id: uuid.UUID | None = None
    password: str | None = None
    is_active: bool | None = None

class UserRead(UserBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    is_active: bool
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str
    tenant_slug: str | None = None
    branch_id: str | None = None

class TokenPayload(BaseModel):
    sub: str
    tenant_id: str
    branch_id: str | None = None
    exp: int

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
