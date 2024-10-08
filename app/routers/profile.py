"""
Routes for profile retrieval
"""
import base64
import datetime
import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import LimitOffsetPage
from fastapi_pagination.ext.sqlmodel import paginate
from pydantic import BaseModel, field_serializer

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

    portfolio_value: float = 0.0
    n_cartridges_created: int
    n_cartridges_collected: int
    n_tapes_created: int
    n_tapes_collected: int
    n_console_achievements: int

    rives_points: int = 0


@router.get(
    '/agg/profile',
)
def list_profiles(
    session: Session = Depends(get_session),
) -> LimitOffsetPage[ProfileResponse]:

    query = (
        select(
            models.Profile.address,
        )
    )

    col_profile = query.selected_columns['address']

    query = query.add_columns(
        # Collected Tapes
        select(func.count(models.CollectedTapes.tape_id))
        .where(models.CollectedTapes.profile_address == col_profile)
        .scalar_subquery().label('n_tapes_collected'),
        # Collected Cartridges
        select(func.count(models.CollectedCartridges.cartridge_id))
        .where(models.CollectedCartridges.profile_address == col_profile)
        .scalar_subquery().label('n_cartridges_collected'),
        # Collected Tapes
        select(func.count(models.Tape.id))
        .where(models.Tape.creator_address == col_profile)
        .scalar_subquery().label('n_tapes_created'),
        # Collected Cartridges
        select(func.count(models.Cartridge.id))
        .where(models.Cartridge.creator_address == col_profile)
        .scalar_subquery().label('n_cartridges_created'),
        # Number of achievements
        select(func.count(models.AwardedConsoleAchievement.id))
        .where(models.AwardedConsoleAchievement.profile_address == col_profile)
        .scalar_subquery().label('n_console_achievements'),
        # Total points from achievements
        select(
            func.coalesce(func.sum(models.AwardedConsoleAchievement.points), 0)
        )
        .where(models.AwardedConsoleAchievement.profile_address == col_profile)
        .scalar_subquery().label('rives_points'),
    )

    query = query.order_by(query.selected_columns['rives_points'].desc())
    return paginate(session, query)


@router.get(
    '/agg/profile/{address}',
    response_model=ProfileResponse,
)
def get_profile(
    address: str,
    session: Session = Depends(get_session),
):
    address = address.lower()
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
    image_data: bytes | None = None
    image_type: str | None = None

    @field_serializer('image_data', when_used='json-unless-none')
    def serialize_image_data(self, value: bytes, _info):
        return base64.b64encode(value)


@router.get(
    '/agg/profile/{address}/console_achievements',
)
def get_profile_achievements(
    address: str,
    session: Session = Depends(get_session),
) -> LimitOffsetPage[AchievementResponse]:
    address = address.lower()
    query = (
        select(
            models.AwardedConsoleAchievement.ca_slug,
            models.ConsoleAchievement.name,
            models.ConsoleAchievement.description,
            models.ConsoleAchievement.image_data,
            models.ConsoleAchievement.image_type,
            models.AwardedConsoleAchievement.created_at,
            models.AwardedConsoleAchievement.points,
            models.AwardedConsoleAchievement.comments,
            models.AwardedConsoleAchievement.tape_id,
        )
        .join(models.AwardedConsoleAchievement.achievement)
        .where(models.AwardedConsoleAchievement.profile_address == address)
        .order_by(models.AwardedConsoleAchievement.created_at.desc())
    )
    return paginate(session, query)


class SummarizedConsoleAchievement(BaseModel):
    ca_slug: str
    latest: datetime.datetime
    total_points: int
    count: int
    name: str | None
    description: str | None
    image_data: bytes | None
    image_type: str | None

    @field_serializer('image_data', when_used='json-unless-none')
    def serialize_image_data(self, value: bytes, _info):
        return base64.b64encode(value)


@router.get(
    '/agg/profile/{address}/console_achievements_summary',
)
def get_profile_achievements_summary(
    address: str,
    session: Session = Depends(get_session),
) -> LimitOffsetPage[SummarizedConsoleAchievement]:
    address = address.lower()
    cte = (
        select(
            models.AwardedConsoleAchievement.ca_slug,
            (
                func.max(models.AwardedConsoleAchievement.created_at)
                .label('latest')
            ),
            (
                func.sum(models.AwardedConsoleAchievement.points)
                .label('total_points')
            ),
            (
                func.count(models.AwardedConsoleAchievement.ca_slug)
                .label('count')
            ),
        )
        .where(models.AwardedConsoleAchievement.profile_address == address)
        .group_by(models.AwardedConsoleAchievement.ca_slug)
        .cte()
    )

    query = (
        select(
            cte,
            models.ConsoleAchievement.name,
            models.ConsoleAchievement.description,
            models.ConsoleAchievement.image_data,
            models.ConsoleAchievement.image_type,
        )
        .join(models.ConsoleAchievement)
        .order_by(cte.c.latest.desc())
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
