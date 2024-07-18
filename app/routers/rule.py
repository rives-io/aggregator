"""
Routes for rule handling
"""
from fastapi import APIRouter, Depends

from sqlmodel import Session

from ..db import models
from ..db.session import get_session, create_or_update

router = APIRouter(tags=['rule'])


@router.put(
    '/agg_rw/rule',
    summary='Create or update a rule',
    response_model=models.Rule,
)
def create_or_update_rule(
    rule: models.Rule,
    session: Session = Depends(get_session),
):
    if rule.cartridge_id is not None:
        create_or_update(models.Cartridge(id=rule.cartridge_id), session)

    return create_or_update(rule, session)
