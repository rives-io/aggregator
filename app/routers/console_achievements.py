"""
Routes for Console Achievements handling
"""
import datetime

from fastapi import APIRouter, Depends, HTTPException

from fastapi_pagination import LimitOffsetPage
from fastapi_pagination.ext.sqlmodel import paginate
from sqlmodel import SQLModel, Session, select, Field

from ..db import models
from ..db.session import get_session, create_or_update

router = APIRouter(tags=['console_achievements'])


@router.get(
    '/agg/console_achievement',
    summary='List existing Console Achievements',
)
def list_console_achievements(
    session: Session = Depends(get_session),
) -> LimitOffsetPage[models.ConsoleAchievement]:
    query = select(models.ConsoleAchievement)
    return paginate(session, query)


@router.get(
    '/agg/console_achievement/{slug}',
    summary='List existing Console Achievements',
    response_model=models.ConsoleAchievement,
)
def get_console_achievement(
    slug: str,
    session: Session = Depends(get_session),
):
    result = session.get(models.ConsoleAchievement, slug)

    if result is None:
        raise HTTPException(status_code=404, detail='Not Found')

    return result


@router.put(
    '/agg_rw/console_achievement',
    summary='Create or update a Console Achievement',
    response_model=models.ConsoleAchievement,
)
def create_or_update_ca(
    console_achievement: models.ConsoleAchievement,
    session: Session = Depends(get_session),
):
    return create_or_update(console_achievement, session)


class AwardedConsoleAchievementCreate(SQLModel):
    profile_address: str
    ca_slug: str
    created_at: datetime.datetime = Field(
        default_factory=datetime.datetime.now
    )
    points: int
    comments: str | None = None


@router.post(
    '/agg_rw/awarded_console_achievement',
    summary='Award someone a Console Achievement',
    response_model=models.AwardedConsoleAchievement,
)
def create_or_update_award(
    award: AwardedConsoleAchievementCreate,
    session: Session = Depends(get_session),
):
    create_or_update(
        models.Profile(address=award.profile_address),
        session,
    )

    new_record = models.AwardedConsoleAchievement.parse_obj(award)

    session.add(new_record)
    session.commit()
    session.refresh(new_record)

    return new_record
