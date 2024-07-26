"""
Routes for profile retrieval
"""
import datetime
import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import LimitOffsetPage
from fastapi_pagination.customization import CustomizedPage, UseModelConfig
from fastapi_pagination.ext.sqlmodel import paginate
from pydantic import BaseModel

from sqlmodel import Session, select, func

from ..db import models
from ..db.session import get_session, create_or_update

logger = logging.getLogger(__name__)

router = APIRouter(tags=['profiles', ])


class Tape(BaseModel):
    tape_id: str
    rule_id: str
    outcard_hash: str
    score: int | None = None
    creator: str
    title: str | None = None
    n_collected: int
    buy_value: int
    sell_value: int
    rank: int


class Cartridge(BaseModel):
    cartridge_id: str
    name: str
    creator: str
    authors: list[str]
    created_at: datetime.datetime
    cover: str | None


class ProfileResponse(BaseModel):
    address: str

    portfolio_value: float
    n_cartridges_created: int
    n_cartridges_collected: int
    n_tapes_created: int
    n_tapes_collected: int
    n_console_achievements: int

    rives_points: int


@router.get(
    '/agg/profile/{address}',
    response_model=ProfileResponse,
)
def get_profile(
    address: str,
    session: Session = Depends(get_session),
):

    stmt = (
        select(
            models.Profile.address,
            models.Profile.points,
        )
        .where(models.Profile.address == address)
    )

    col_profile = stmt.selected_columns['address']

    stmt = stmt.add_columns(
        # Collected Tapes
        select(func.count(models.CollectedTapes.tape_id))
        .where(models.CollectedTapes.profile_address == col_profile)
        .scalar_subquery().label('n_collected_tapes'),
        # Collected Cartridges
        select(func.count(models.CollectedCartridges.cartridge_id))
        .where(models.CollectedCartridges.profile_address == col_profile)
        .scalar_subquery().label('n_collected_cartridges'),
        # Collected Tapes
        select(func.count(models.Tape.id))
        .where(models.Tape.creator_address == col_profile)
        .scalar_subquery().label('n_created_tapes'),
        # Collected Cartridges
        select(func.count(models.Cartridge.id))
        .where(models.Cartridge.creator_address == col_profile)
        .scalar_subquery().label('n_created_cartridges'),
        # Number of achievements
        select(func.count(models.AwardedConsoleAchievement.id))
        .where(models.AwardedConsoleAchievement.profile_address == col_profile)
        .scalar_subquery().label('n_console_achievements'),
        # Total points from achievements
        select(func.sum(models.AwardedConsoleAchievement.points))
        .where(models.AwardedConsoleAchievement.profile_address == col_profile)
        .scalar_subquery().label('total_points'),
    )

    logger.info("Executing query %s", str(stmt))
    resp = session.execute(stmt).one_or_none()

    if resp is None:
        raise HTTPException(status_code=404, detail='Profile not found.')

    return ProfileResponse(
        address=address,
        portfolio_value=0,
        n_cartridges_created=resp.n_created_cartridges,
        n_cartridges_collected=resp.n_collected_cartridges,
        n_tapes_created=resp.n_created_tapes,
        n_tapes_collected=resp.n_collected_tapes,
        n_console_achievements=resp.n_console_achievements,
        rives_points=resp.total_points or 0,
    )


class AchievementResponse(BaseModel):
    ca_slug: str | None = None
    name: str | None = None
    description: str | None = None
    created_at: datetime.datetime | None = None
    points: int = 0
    comments: str | None = None
    tape_id: str | None = None


ProfileAchievementPage = CustomizedPage[
    LimitOffsetPage,
    UseModelConfig(extra='allow')
]


@router.get(
    '/agg/profile/{address}/console_achievements',
)
def get_profile_achievements(
    address: str,
    session: Session = Depends(get_session),
) -> ProfileAchievementPage[AchievementResponse]:

    query = (
        select(
            models.AwardedConsoleAchievement.ca_slug,
            models.ConsoleAchievement.name,
            models.ConsoleAchievement.description,
            models.AwardedConsoleAchievement.created_at,
            models.AwardedConsoleAchievement.points,
            models.AwardedConsoleAchievement.comments,
            models.AwardedConsoleAchievement.tape_id,
        )
        .join(models.AwardedConsoleAchievement.achievement)
        .where(models.AwardedConsoleAchievement.profile_address == address)
    )
    return paginate(session, query)


@router.put(
    '/agg_rw/profile',
    summary='Create or do Partial Update on a Profile record',
    response_model=models.Profile,
)
def create_or_update_profile(
    profile: models.Profile,
    session: Session = Depends(get_session),
):
    return create_or_update(profile, session)
