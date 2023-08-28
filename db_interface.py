from sqlalchemy import (create_engine, Table,
                        Integer, Column,
                        MetaData, inspect,
                        select, delete, insert)
from consts import DB_PATH

engine = create_engine(f'sqlite:///{DB_PATH}', echo=True)
conn = engine.connect()
metadata = MetaData()

student_groups = Table(
    'student_groups',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('course', Integer, nullable=False),
)


def init_database():
    if not inspect(engine).has_table('student_groups'):
        student_groups.create(engine)


def ids_by_course(course: int):
    return zip(
        *conn.execute(
            select(student_groups.c.id).where(
                student_groups.c.course == course
            )
        ).all()
    )[0]


def delete_group(group_id: int):
    conn.execute(delete(student_groups).where(student_groups.c.id == group_id))
    conn.commit()


def groups_ids():
    return zip(*conn.execute(select(student_groups.c.id)).all())[0]


def add_group(group_id: int, course: int):
    conn.execute(insert(student_groups), [{
        'id': group_id,
        'course': course,
    }])
    conn.commit()
