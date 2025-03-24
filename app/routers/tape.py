"""
Routes for profile retrieval
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from sqlmodel import Session

from ..db import models
from ..db.session import get_session, create_or_update

router = APIRouter(tags=['tapes'])


@router.put(
    '/agg_rw/tape',
    summary='Create or update a tape',
    response_model=models.Tape,
)
def create_or_update_tape(
    tape: models.Tape,
    session: Session = Depends(get_session),
):
    if tape.creator_address is not None:
        create_or_update(models.Profile(address=tape.creator_address), session)

    if tape.rule_id is not None:
        create_or_update(models.Rule(id=tape.rule_id), session)

    return create_or_update(tape, session)


@router.put(
    '/agg_rw/collected_tape',
    summary='Create or update a collected tape',
    response_model=models.CollectedTapes,
)
def create_or_update_collected_tape(
    collected_tape: models.CollectedTapes,
    session: Session = Depends(get_session),
):
    create_or_update(
        models.Profile(address=collected_tape.profile_address),
        session,
    )

    create_or_update(
        models.Tape(id=collected_tape.tape_id),
        session,
    )

    return create_or_update(collected_tape, session)

@router.get(
    '/agg/tape/{tape_id}',
    summary='Get tape data',
    response_model=models.Tape,
)
def get_tape(
    tape_id: str,
    session: Session = Depends(get_session),
):
    tape = session.get(models.Tape, tape_id)
    if tape is None:
        raise HTTPException(status_code=404, detail='Tape not found.')
    return tape
