"""
Routes for Notification
"""
import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse

from fastapi_pagination import LimitOffsetPage
from fastapi_pagination.ext.sqlmodel import paginate
from pydantic import BaseModel
from sqlmodel import Session, select

from ..db import models
from ..db.session import get_session, create_or_update

router = APIRouter(tags=['notifications'])


class NotificationBase(BaseModel):
    created_at: datetime.datetime
    title: str | None = None
    message: str
    url: str | None = None
    unread: bool = True


class NotificationView(NotificationBase):
    id: int


class NotificationCreate(NotificationBase):
    profile_address: str


@router.get(
    '/agg/notifications/{address}',
    summary='Get notifications for the given user by address',
)
def list_notifications(
    address: str,
    unread: bool | None = None,
    session: Session = Depends(get_session),
) -> LimitOffsetPage[NotificationView]:

    query = (
        select(models.Notification)
        .where(models.Notification.profile_address == address.lower())
    )

    if unread is not None:
        query = query.where(models.Notification.unread == unread)

    query = (
        query
        .order_by(models.Notification.created_at.desc())
    )
    return paginate(session, query)


@router.get(
    '/agg/notifications/{address}/{notification_id}',
    summary='Follow notification and mark as read',
)
def follow_notifications(
    address: str,
    notification_id: int,
    session: Session = Depends(get_session),
):
    query = (
        select(models.Notification)
        .where(models.Notification.profile_address == address.lower())
        .where(models.Notification.id == notification_id)
    )
    notification = session.exec(query).one_or_none()

    if notification is None:
        raise HTTPException(status_code=404, detail='Not Found')

    if notification.unread:
        notification.unread = False
        session.add(notification)
        session.commit()

    return RedirectResponse(notification.url)


@router.put(
    '/agg_rw/notifications',
    summary='Create a Notification',
)
def create_notifications(
    notification: NotificationCreate,
    session: Session = Depends(get_session),
) -> NotificationView:

    profile_address = notification.profile_address.lower()
    notification.profile_address = profile_address

    create_or_update(
        models.Profile(address=profile_address),
        session
    )

    new_notification = models.Notification.model_validate(notification)
    return create_or_update(new_notification, session)
