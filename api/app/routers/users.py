import json
from datetime import datetime, UTC

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.app.core.database import get_db
from api.app.dependencies.auth import get_current_user
from api.app.models.user import User
from api.app.schemas.user import UserUpdate, UserMeResponse
from api.app.services.export import build_export

router = APIRouter(prefix="/api/v1/users", tags=["users"])

# Valid IANA timezones (simplified check — full validation via zoneinfo)
def _validate_timezone(tz: str) -> bool:
    try:
        import zoneinfo
        zoneinfo.ZoneInfo(tz)
        return True
    except Exception:
        return False


@router.get("/me", response_model=UserMeResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserMeResponse)
async def update_me(
    body: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if body.timezone is not None:
        if not _validate_timezone(body.timezone):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid timezone string",
            )
        current_user.timezone = body.timezone

    if body.preferences is not None:
        merged = dict(current_user.preferences or {})
        merged.update(body.preferences)
        current_user.preferences = merged

    current_user.updated_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.get("/me/export")
async def export_me(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = await build_export(current_user, db)
    content = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)
    return Response(
        content=content,
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=hyppo-export.json"},
    )
