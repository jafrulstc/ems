from pydantic import BaseModel, EmailStr, ConfigDict
import uuid
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    user_type: str
    branch_id: Optional[uuid.UUID] = None
    role_id: Optional[uuid.UUID] = None

class UserCreate(UserBase):
    password: str

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
