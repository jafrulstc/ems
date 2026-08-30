from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import event
from sqlalchemy.orm import with_loader_criteria, Session
from app.core.config import settings
from app.db.base import Base, SoftDeleteMixin, TenantMixin
from app.core.context import tenant_context, user_context

engine = create_async_engine(settings.DATABASE_URL, echo=True, future=True)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

@event.listens_for(Session, "do_orm_execute")
def _add_filtering_criteria(execute_state):
    # Only apply to SELECT and allow skipping via execution_options
    if execute_state.is_select and not execute_state.execution_options.get("skip_rlac", False):
        tenant_id = tenant_context.get()
        user = user_context.get()

        # 1. Soft Delete Filter
        execute_state.statement = execute_state.statement.options(
            with_loader_criteria(
                SoftDeleteMixin,
                lambda cls: cls.is_deleted == False,
                include_aliases=True,
            )
        )

        # 2. Tenant Filter
        if tenant_id:
            execute_state.statement = execute_state.statement.options(
                with_loader_criteria(
                    TenantMixin,
                    lambda cls: cls.tenant_id == tenant_id,
                    include_aliases=True,
                )
            )

        # 3. RLAC (Row-Level Access Control) for Branch Admin
        if user and hasattr(user, 'user_type') and user.user_type == "branch_admin" and hasattr(user, 'branch_id') and user.branch_id:
            execute_state.statement = execute_state.statement.options(
                with_loader_criteria(
                    Base,
                    lambda cls: cls.branch_id == user.branch_id if hasattr(cls, "branch_id") else True,
                    include_aliases=True,
                )
            )

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
