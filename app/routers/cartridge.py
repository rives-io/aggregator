"""
Routes for cartridge handling
"""
from fastapi import APIRouter, Depends

from sqlmodel import Session

from ..db import models
from ..db.session import get_session, create_or_update

router = APIRouter(tags=['cartridge'])


@router.put(
    '/cartridge',
    summary='Create or update a cartridge',
    response_model=models.Cartridge,
)
def create_or_update_cartridge(
    cartridge: models.Cartridge,
    session: Session = Depends(get_session),
):
    if cartridge.creator_address is not None:
        create_or_update(models.Profile(address=cartridge.creator_address),
                         session)

    return create_or_update(cartridge, session)


@router.put(
    '/collected_cartridge',
    summary='Create or update a collected cartridge',
    response_model=models.CollectedCartridges,
)
def create_or_update_collected_cartridge(
    collected_cartridge: models.CollectedCartridges,
    session: Session = Depends(get_session),
):
    create_or_update(
        models.Profile(address=collected_cartridge.profile_address),
        session,
    )

    create_or_update(
        models.Cartridge(id=collected_cartridge.cartridge_id),
        session,
    )

    return create_or_update(collected_cartridge, session)
