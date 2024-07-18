"""
Routes for profile retrieval
"""
import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from sqlmodel import Session, select, func

from ..db import models
from ..db.session import get_session, create_or_update

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

    rives_points: int


@router.get(
    '/agg/profile/{address}',
    # response_model=models.Profile,
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
    )

    resp = session.execute(stmt).one_or_none()

    if resp is None:
        raise HTTPException(status_code=404, detail='Profile not found.')
    return resp
    resp = resp._mapping

    return ProfileResponse(
        wallet=address,
        portfolio_value=250,
        n_cartridges_created=2,
        n_cartridges_collected=3,
        n_tapes_created=4,
        n_tapes_collected=5,
        rives_points=1234,
    )


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
