from pydantic import BaseModel, ConfigDict
import uuid
from datetime import datetime

class InstituteBase(BaseModel):
    name: str
    slug: str
    address: str | None = None
    contact_email: str | None = None

class InstituteCreate(InstituteBase):
    admin_email: str
    admin_password: str

class InstituteUpdate(InstituteBase):
    admin_email: str | None = None
    admin_password: str | None = None

class InstituteRead(InstituteBase):
    id: uuid.UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class BranchBase(BaseModel):
    name: str
    address: str | None = None

class BranchCreate(BranchBase):
    pass

class BranchRead(BranchBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
