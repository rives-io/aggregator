"""
Routes for rule handling
"""
import base64
import datetime

from fastapi import APIRouter, Depends, HTTPException, Response, UploadFile
from pydantic import BaseModel, field_validator, field_serializer
from sqlmodel import Session, select, exists

from ..db import models
from ..db.session import get_session, create_or_update
from ..file_signatures import guess_mime_type
from .console_achievements import ConsoleAchievementAPI

router = APIRouter(tags=['rule'])


class RuleInput(BaseModel):
    id: str
    name: str | None = None
    description: str | None = None
    created_at: datetime.datetime | None = None

    start: datetime.datetime | None = None
    end: datetime.datetime | None = None

    cartridge_id: str | None = None

    created_by: str | None = None

    sponsor_name: str | None = None
    sponsor_image_data: bytes | None = None
    sponsor_image_type: str | None = None

    prize: str | None = None

    @field_validator('sponsor_image_data', mode='before')
    @classmethod
    def validate_image_data(cls, value: str | bytes | None) -> bytes | None:
        if value is None:
            return
        if isinstance(value, bytes):
            return value
        return base64.b64decode(value)

    @field_serializer('sponsor_image_data', when_used='json-unless-none')
    def serialize_image_data(self, value: bytes, _info):
        return base64.b64encode(value)


@router.put(
    '/agg_rw/rule',
    summary='Create or update a rule',
    response_model=RuleInput,
)
def create_or_update_rule(
    rule: RuleInput,
    session: Session = Depends(get_session),
):
    if rule.cartridge_id is not None:
        create_or_update(models.Cartridge(id=rule.cartridge_id), session)

    if (
        (rule.sponsor_image_data is not None)
        and (rule.sponsor_image_type is None)
    ):
        rule.sponsor_image_type = guess_mime_type(rule.sponsor_image_data)
    rule_model = models.Rule.model_validate(rule)
    return create_or_update(rule_model, session)


class RuleResponse(BaseModel):
    id: str
    name: str | None
    description: str | None
    created_at: datetime.datetime | None

    start: datetime.datetime | None
    end: datetime.datetime | None

    cartridge_id: str | None

    sponsor_name: str | None = None
    sponsor_image_data: bytes | None = None
    sponsor_image_type: str | None = None

    prize: str | None = None

    achievements: list[ConsoleAchievementAPI]

    @field_serializer('sponsor_image_data', when_used='json-unless-none')
    def serialize_image_data(self, value: bytes, _info):
        return base64.b64encode(value)


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


@router.get(
    '/agg/rule/{rule_id}/sponsor_image',
    summary='Display sponsor image',
)
def get_sponsor_image(
    rule_id: str,
    session: Session = Depends(get_session),
):
    result = session.get(models.Rule, rule_id)

    if result is None:
        raise HTTPException(status_code=404, detail='Not Found')

    return Response(content=result.sponsor_image_data,
                    media_type=result.sponsor_image_type)


@router.put('/agg_rw/rule/{rule_id}/sponsor_image')
def upload_sponsor_image(
    rule_id: str,
    uploaded: UploadFile,
    session: Session = Depends(get_session),
):
    # Get achievement
    rule = session.get(models.Rule, rule_id)

    if rule is None:
        raise HTTPException(status_code=404)

    data = uploaded.file.read()
    mime_type = guess_mime_type(data)

    rule.sponsor_image_data = data
    rule.sponsor_image_type = mime_type

    session.add(rule)
    session.commit()
    return {'status': 'Ok'}
