"""
Core feature router — Academic Years, Menus, Settings, Geo.
Prefix: /api/v1/core  (set in main.py)
"""
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, get_organization_id, require_permission
from app.features.core.schemas import (
    AcademicYearCreate, AcademicYearRead, AcademicYearUpdate,
    AppSettingCreate, AppSettingRead, AppSettingUpdate,
    DistrictRead, DivisionRead, MenuCreate, MenuRead, MenuUpdate,
    PostOfficeRead, UpazilaRead, VillageRead,
)
from app.features.core.services.academic_year_service import AcademicYearService
from app.features.core.services.geo_service import GeoService
from app.features.core.services.menu_service import MenuService
from app.features.core.services.settings_service import SettingsService
from app.shared.pagination import PaginationParams, pagination_params
from app.shared.schemas import APIResponse, PaginatedResponse, ok, paginated

router = APIRouter()

# ── Academic Years ────────────────────────────────────────────────────────────

@router.get("/academic-years", response_model=PaginatedResponse[AcademicYearRead], tags=["Academic Years"])
async def list_academic_years(
    p: PaginationParams = Depends(pagination_params),
    org_id: int = Depends(get_organization_id),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_permission("core.academic_years.view")),
):
    svc = AcademicYearService(db)
    data = await svc.list(org_id, p)
    return paginated(data.items, data.total, data.page, data.size)


@router.post("/academic-years", response_model=APIResponse[AcademicYearRead], status_code=201, tags=["Academic Years"])
async def create_academic_year(
    payload: AcademicYearCreate,
    org_id: int = Depends(get_organization_id),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_permission("core.academic_years.create")),
):
    svc = AcademicYearService(db)
    return ok(await svc.create(org_id, payload), "Academic year created.")


@router.get("/academic-years/{id}", response_model=APIResponse[AcademicYearRead], tags=["Academic Years"])
async def get_academic_year(
    id: int, org_id: int = Depends(get_organization_id), db: AsyncSession = Depends(get_db),
    _: None = Depends(require_permission("core.academic_years.view")),
):
    return ok(await AcademicYearService(db).get(id, org_id))


@router.put("/academic-years/{id}", response_model=APIResponse[AcademicYearRead], tags=["Academic Years"])
async def update_academic_year(
    id: int, payload: AcademicYearUpdate,
    org_id: int = Depends(get_organization_id), db: AsyncSession = Depends(get_db),
    _: None = Depends(require_permission("core.academic_years.edit")),
):
    return ok(await AcademicYearService(db).update(id, org_id, payload))


@router.delete("/academic-years/{id}", response_model=APIResponse[None], tags=["Academic Years"])
async def delete_academic_year(
    id: int, org_id: int = Depends(get_organization_id), db: AsyncSession = Depends(get_db),
    _: None = Depends(require_permission("core.academic_years.delete")),
):
    await AcademicYearService(db).delete(id, org_id)
    return ok(None, "Academic year deleted.")


# ── Menus ─────────────────────────────────────────────────────────────────────

@router.get("/menus", response_model=APIResponse[list[MenuRead]], tags=["Menus"])
async def list_menus(
    flat: bool = False,
    org_id: int = Depends(get_organization_id),
    db: AsyncSession = Depends(get_db),
):
    svc = MenuService(db)
    data = await svc.get_flat(org_id) if flat else await svc.get_tree(org_id)
    return ok(data)


@router.post("/menus", response_model=APIResponse[MenuRead], status_code=201, tags=["Menus"])
async def create_menu(
    payload: MenuCreate, org_id: int = Depends(get_organization_id), db: AsyncSession = Depends(get_db),
    _: None = Depends(require_permission("core.menus.create")),
):
    return ok(await MenuService(db).create(org_id, payload), "Menu item created.")


@router.put("/menus/{id}", response_model=APIResponse[MenuRead], tags=["Menus"])
async def update_menu(
    id: int, payload: MenuUpdate,
    org_id: int = Depends(get_organization_id), db: AsyncSession = Depends(get_db),
    _: None = Depends(require_permission("core.menus.edit")),
):
    return ok(await MenuService(db).update(id, org_id, payload))


@router.delete("/menus/{id}", response_model=APIResponse[None], tags=["Menus"])
async def delete_menu(
    id: int, org_id: int = Depends(get_organization_id), db: AsyncSession = Depends(get_db),
    _: None = Depends(require_permission("core.menus.delete")),
):
    await MenuService(db).delete(id, org_id)
    return ok(None, "Menu item deleted.")


# ── Settings ──────────────────────────────────────────────────────────────────

@router.get("/settings", response_model=APIResponse[list[AppSettingRead]], tags=["Settings"])
async def list_settings(
    org_id: int = Depends(get_organization_id), db: AsyncSession = Depends(get_db),
    _: None = Depends(require_permission("core.settings.view")),
):
    return ok(await SettingsService(db).list(org_id))


@router.post("/settings", response_model=APIResponse[AppSettingRead], status_code=201, tags=["Settings"])
async def create_setting(
    payload: AppSettingCreate, org_id: int = Depends(get_organization_id), db: AsyncSession = Depends(get_db),
    _: None = Depends(require_permission("core.settings.create")),
):
    return ok(await SettingsService(db).create(org_id, payload), "Setting created.")


@router.put("/settings/{key}", response_model=APIResponse[AppSettingRead], tags=["Settings"])
async def update_setting(
    key: str, payload: AppSettingUpdate,
    org_id: int = Depends(get_organization_id), db: AsyncSession = Depends(get_db),
    _: None = Depends(require_permission("core.settings.edit")),
):
    return ok(await SettingsService(db).update(org_id, key, payload))


# ── Geo (public) ──────────────────────────────────────────────────────────────

@router.get("/geo/divisions", response_model=APIResponse[list[DivisionRead]], tags=["Geo"])
async def list_divisions(db: AsyncSession = Depends(get_db)):
    return ok(await GeoService(db).get_divisions())


@router.get("/geo/districts", response_model=APIResponse[list[DistrictRead]], tags=["Geo"])
async def list_districts(division_id: Optional[int] = None, db: AsyncSession = Depends(get_db)):
    return ok(await GeoService(db).get_districts(division_id))


@router.get("/geo/upazilas", response_model=APIResponse[list[UpazilaRead]], tags=["Geo"])
async def list_upazilas(district_id: Optional[int] = None, db: AsyncSession = Depends(get_db)):
    return ok(await GeoService(db).get_upazilas(district_id))


@router.get("/geo/post-offices", response_model=APIResponse[list[PostOfficeRead]], tags=["Geo"])
async def list_post_offices(upazila_id: Optional[int] = None, db: AsyncSession = Depends(get_db)):
    return ok(await GeoService(db).get_post_offices(upazila_id))


@router.get("/geo/villages", response_model=APIResponse[list[VillageRead]], tags=["Geo"])
async def list_villages(post_office_id: Optional[int] = None, db: AsyncSession = Depends(get_db)):
    return ok(await GeoService(db).get_villages(post_office_id))
