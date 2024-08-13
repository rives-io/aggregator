"""
Routes for rule handling
"""
import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select, exists

from ..db import models
from ..db.session import get_session, create_or_update

from .console_achievements import ConsoleAchievementAPI

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


class RuleResponse(BaseModel):
    id: str
    name: str | None
    description: str | None
    created_at: datetime.datetime | None

    start: datetime.datetime | None
    end: datetime.datetime | None

    cartridge_id: str | None

    achievements: list[ConsoleAchievementAPI]


@router.get(
    '/agg/rule/{rule_id}',
    summary='Get details for a rule',
    response_model=RuleResponse,
)
def get_rule(
    rule_id: str,
    session: Session = Depends(get_session),
):
    rule = session.get(models.Rule, rule_id)
    if rule is None:
        raise HTTPException(status_code=404, detail='Rule not found.')
    return rule


class AddRuleConsoleAchievementLink(BaseModel):
    ca_slug: str


@router.put(
    '/agg_rw/rule/{rule_id}/achievement',
    summary='Assign an achievement to this rule',
    response_model=models.RuleConsoleAchievement,
    description=(
        "This endpoint will create a rule if it doesn't already exist. However"
        " the achievement must have already been created."
    )
)
def assign_achievement_rule(
    rule_id: str,
    link: AddRuleConsoleAchievementLink,
    session: Session = Depends(get_session),
):
    ca_exists = session.exec(
        select(
            exists()
            .where(
                models.ConsoleAchievement.slug == link.ca_slug)  # type:ignore
        )
    ).one()
    print(f'{ca_exists=}')
    if not ca_exists:
        raise HTTPException(status_code=404,
                            detail='Console Achievement not found.')
    create_or_update(models.Rule(id=rule_id), session)
    instance = models.RuleConsoleAchievement(
        rule_id=rule_id,
        ca_slug=link.ca_slug,
    )
    return create_or_update(instance, session)
