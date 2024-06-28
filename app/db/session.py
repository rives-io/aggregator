from functools import lru_cache

from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError
from sqlmodel import create_engine, SQLModel, Session

from ..config import settings


@lru_cache
def get_engine():
    engine = create_engine(
        settings.db_url,
        echo=True,
    )
    return engine


def create_db_and_tables():
    engine = get_engine()
    SQLModel.metadata.create_all(engine)


def get_session():
    engine = get_engine()
    with Session(engine) as session:
        yield session


def _get_pk_dict(instance: SQLModel):
    insp = inspect(instance)

    pk_fields = [x.name for x in insp.mapper.primary_key]

    return {
        field: getattr(instance, field)
        for field in pk_fields
    }


def create_or_update(instance: SQLModel, session: Session):

    insp = inspect(instance)
    assert insp.session is None

    # Try the create route
    try:
        session.add(instance)
        session.commit()
        session.refresh(instance)
        return instance
    except IntegrityError as exc:
        session.rollback()

        # Profile probably already exists. Let's try to get it
        instance_pk = _get_pk_dict(instance)
        model = insp.class_

        db_record = session.get(model, instance_pk)

        if db_record is None:
            # This is another error
            raise exc

    # Try the partial update flow
    update_data = instance.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_record, field, value)

    session.add(db_record)
    session.commit()
    session.refresh(db_record)
    return db_record
