import logging
from functools import wraps
from typing import Iterable

from sqlalchemy import Column, Integer
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import delete, insert, select, update

from app.exceptions import DBError
from settings import DB_PATH

Base = declarative_base()
engine = create_async_engine(DB_PATH, echo=True, pool_pre_ping=True)
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)


class StudentGroup(Base):  # type: ignore[valid-type,misc]
    __tablename__ = "student_groups"

    id = Column(Integer, primary_key=True)
    course = Column(Integer, nullable=False)


def db_connect(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        async with SessionLocal() as session:
            try:
                return await func(*args, session=session, **kwargs)
            except DBAPIError as err:
                logging.error("Database error")
                raise DBError() from err
            except Exception as err:
                logging.critical("Unexpected error")
                raise DBError() from err

    return wrapper


@db_connect
async def delete_group(group_id: int, *, session: AsyncSession) -> None:
    await session.execute(
        delete(StudentGroup).where(StudentGroup.id == group_id)  # type: ignore
    )
    await session.commit()


@db_connect
async def get_group_ids_by_course(
    course: int, *, session: AsyncSession
) -> Iterable[int]:
    group_ids = await session.execute(
        select(StudentGroup).where(StudentGroup.course == course)
    )
    return [group_id[0].id for group_id in group_ids]


@db_connect
async def get_course_by_group_id(
    group_id: int, *, session: AsyncSession
) -> int | None:
    course: int | None = await session.scalar(
        select(StudentGroup.course).where(StudentGroup.id == group_id)
    )
    return course


@db_connect
async def get_groups_ids(*, session: AsyncSession) -> Iterable[int]:
    group_ids = (await session.execute(select(StudentGroup))).all()
    return [group_id[0].id for group_id in group_ids]


@db_connect
async def add_group(
    group_id: int, course: int, *, session: AsyncSession
) -> None:
    await session.execute(
        insert(StudentGroup),  # type: ignore
        [
            {
                "id": group_id,
                "course": course,
            }
        ],
    )
    await session.commit()


@db_connect
async def change_group_course(
    group_id: int, course: int, *, session: AsyncSession
) -> None:
    await session.execute(
        update(StudentGroup)  # type: ignore
        .where(StudentGroup.id == group_id)
        .values(course=course)
    )
    await session.commit()
