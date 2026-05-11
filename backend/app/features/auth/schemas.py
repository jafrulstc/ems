"""Pydantic schemas for the Auth feature."""
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


# ── Auth / Token ──────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    org_slug: str
    email: str  # str not EmailStr — allows internal .local domains
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ── Permission ────────────────────────────────────────────────────────────────

class PermissionRead(BaseModel):
    id: int
    key: str
    label: str
    module: str
    action: str
    model_config = ConfigDict(from_attributes=True)


class PermissionOverrideUpsert(BaseModel):
    permission_key: str
    is_granted: bool


class PermissionOverrideRead(BaseModel):
    id: int
    user_id: int
    permission_id: int
    is_granted: bool
    model_config = ConfigDict(from_attributes=True)


# ── Role ──────────────────────────────────────────────────────────────────────

class RoleCreate(BaseModel):
    name: str
    description: Optional[str] = None


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class RoleRead(BaseModel):
    id: int
    organization_id: int
    name: str
    description: Optional[str]
    model_config = ConfigDict(from_attributes=True)


class RoleWithPermissions(RoleRead):
    permissions: List[PermissionRead] = []


# ── User ──────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    email: str  # str not EmailStr — allows internal .local domains
    password: str
    username: Optional[str] = None
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False


class UserUpdate(BaseModel):
    username: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None  # plain text; hashed in service


class UserRead(BaseModel):
    id: int
    organization_id: int
    email: str
    username: Optional[str]
    full_name: Optional[str]
    is_active: bool
    is_superuser: bool
    roles: List[RoleRead] = []
    model_config = ConfigDict(from_attributes=True)


class UserMeResponse(UserRead):
    """Extended user info with resolved permission keys for the /auth/me endpoint."""
    permissions: list[str] = []


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead
