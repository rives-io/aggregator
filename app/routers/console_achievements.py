"""
Routes for Console Achievements handling
"""
import base64
import datetime

from fastapi import APIRouter, Depends, HTTPException, UploadFile, Response

from fastapi_pagination import LimitOffsetPage
from fastapi_pagination.ext.sqlmodel import paginate
from pydantic import BaseModel, field_validator, field_serializer
from sqlmodel import Session, select, Field

from ..db import models
from ..db.session import get_session, create_or_update
from ..file_signatures import guess_mime_type

router = APIRouter(tags=['console_achievements'])


class ConsoleAchievementAPI(BaseModel):
    slug: str
    name: str | None = None
    description: str | None = None
    points: int = 0
    image_data: bytes | None = None
    image_type: str | None = None

    @field_validator('image_data', mode='before')
    @classmethod
    def validate_image_data(cls, value: str | bytes | None) -> bytes | None:
        if value is None:
            return
        if isinstance(value, bytes):
            return value
        return base64.b64decode(value)

    @field_serializer('image_data', when_used='json-unless-none')
    def serialize_image_data(self, value: bytes, _info):
        return base64.b64encode(value)


@router.get(
    '/agg/console_achievement',
    summary='List existing Console Achievements',
)
def list_console_achievements(
    session: Session = Depends(get_session),
) -> LimitOffsetPage[ConsoleAchievementAPI]:
    query = select(models.ConsoleAchievement)
    return paginate(session, query)


@router.get(
    '/agg/console_achievement/{slug}',
    summary='List existing Console Achievements',
    response_model=ConsoleAchievementAPI,
)
def get_console_achievement(
    slug: str,
    session: Session = Depends(get_session),
):
    result = session.get(models.ConsoleAchievement, slug)

    if result is None:
        raise HTTPException(status_code=404, detail='Not Found')

    return result


class ConsoleAchievementPlayer(BaseModel):
    profile_address: str | None
    created_at: datetime.datetime | None
    points: int
    tape_id: str | None


@router.get(
    '/agg/console_achievement/{slug}/players',
    summary='List players who unlocked a given Console Achievement',
)
def list_console_achievement_players(
    slug: str,
    session: Session = Depends(get_session),
) -> LimitOffsetPage[ConsoleAchievementPlayer]:
    query = (
        select(
            models.AwardedConsoleAchievement.profile_address,
            models.AwardedConsoleAchievement.created_at,
            models.AwardedConsoleAchievement.points,
            models.AwardedConsoleAchievement.tape_id,
        )
        .where(
            models.AwardedConsoleAchievement.ca_slug == slug
        )
        .order_by(models.AwardedConsoleAchievement.created_at.desc())
    )
    return paginate(session, query)


@router.get(
    '/agg/console_achievement/{slug}/image',
    summary='List existing Console Achievements',
)
def get_console_achievement_image(
    slug: str,
    session: Session = Depends(get_session),
):
    result = session.get(models.ConsoleAchievement, slug)

    if result is None:
        raise HTTPException(status_code=404, detail='Not Found')

    return Response(content=result.image_data, media_type=result.image_type)


@router.put(
    '/agg_rw/console_achievement',
    summary='Create or update a Console Achievement',
    response_model=ConsoleAchievementAPI,
)
def create_or_update_ca(
    ca: ConsoleAchievementAPI,
    session: Session = Depends(get_session),
):
    if (ca.image_data is not None) and (ca.image_type is None):
        ca.image_type = guess_mime_type(ca.image_data)

    console_achievement = models.ConsoleAchievement.model_validate(ca)
    return create_or_update(console_achievement, session)


class AwardedConsoleAchievementCreate(BaseModel):
    profile_address: str
    ca_slug: str
    created_at: datetime.datetime = Field(
        default_factory=datetime.datetime.now
    )
    points: int
    comments: str | None = None
    tape_id: str | None = None


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

    if award.tape_id is not None:
        create_or_update(
            models.Tape(id=award.tape_id),
            session,
        )

    new_record = models.AwardedConsoleAchievement.model_validate(award)

    session.add(new_record)
    session.commit()
    session.refresh(new_record)

    return new_record


@router.put('/agg_rw/console_achievement/{slug}/image')
def upload_image(
    slug: str,
    uploaded: UploadFile,
    session: Session = Depends(get_session),
):
    # Get achievement
    query = (
        select(models.ConsoleAchievement)
        .where(models.ConsoleAchievement.slug == slug)
    )
    achievement = session.exec(query).one_or_none()

    if achievement is None:
        raise HTTPException(status_code=404)

    data = uploaded.file.read()
    mime_type = guess_mime_type(data)

    achievement.image_data = data
    achievement.image_type = mime_type

    session.add(achievement)
    session.commit()
    return {'status': 'Ok'}
