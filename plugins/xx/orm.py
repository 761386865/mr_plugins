from sqlalchemy import create_engine, Engine, or_
from sqlalchemy.orm import sessionmaker, Session

from plugins.xx.exceptions import SqlError
from plugins.xx.utils import *
from plugins.xx.models import Base, Course, Teacher, Config




class DB:
    engine: Engine
    session: Session

    def __init__(self):
        self.engine = create_engine('sqlite:///study.db')
        Base.metadata.create_all(self.engine, checkfirst=True)
        self.session = sessionmaker(bind=self.engine)()


class CourseDB:
    session: Session
    limit: int = 20

    def __init__(self, session: Session):
        self.session = session

    def get_course_by_primary(self, primary: int):
        return self.session.query(Course).filter_by(id=primary).first()

    def get_course_by_code(self, code: str):
        return self.session.query(Course).filter_by(code=code).first()

    def filter_course(self, keyword, status):
        query = self.session.query(Course)
        if keyword:
            rule = or_(Course.code.like(f"%{keyword}%"), Course.casts.like(f"%{keyword}%"))
            query = query.filter(rule)
        if status:
            query = query.filter(Course.status == status)
        return query.order_by(Course.create_time.desc()).all()

    def list_course(self, **qry):
        return self.session.query(Course).filter_by(**qry).all()

    def add_course(self, data: Course):
        course = self.session.query(Course).filter_by(code=data.code).first()
        if course:
            return course
        try:
            data.create_time = get_current_datetime_str()
            self.session.add(data)
            self.session.commit()
            return data
        except Exception as e:
            print(repr(e))
            self.session.rollback()
            raise SqlError

    def update_course(self, data: Course):
        course = self.session.query(Course).filter_by(id=data.id).first()
        if not course:
            return None
        try:
            data.update_time = get_current_datetime_str()
            copy_properties(data, course)
            self.session.commit()
            return course
        except Exception as e:
            print(repr(e))
            self.session.rollback()
            raise SqlError

    def delete_course(self, primary: int):
        course = self.get_course_by_primary(primary)
        if course:
            try:
                self.session.delete(course)
                self.session.commit()
            except Exception as e:
                print(repr(e))
                self.session.rollback()
                raise SqlError


class TeacherDB:
    session: Session

    def __init__(self, session: Session):
        self.session = session

    def get_teacher_by_primary(self, primary: int):
        return self.session.query(Teacher).filter_by(id=primary).first()

    def get_teacher_by_code(self, code: str):
        return self.session.query(Teacher).filter_by(code=code).first()

    def filter_teacher(self, keyword):
        query = self.session.query(Teacher)
        if keyword:
            query = query.filter(Teacher.name.like(f"%{keyword}%"))
        return query.order_by(Teacher.create_time.desc()).all()

    def list_teacher(self, **qry):
        return self.session.query(Teacher).filter_by(**qry).all()

    def add_teacher(self, data: Teacher):
        teacher = self.session.query(Teacher).filter_by(code=data.code).first()
        if teacher:
            return teacher
        try:
            data.create_time = get_current_datetime_str()
            self.session.add(data)
            self.session.commit()
            return data
        except Exception as e:
            print(repr(e))
            self.session.rollback()
            raise SqlError

    def update_teacher(self, data: Teacher):
        teacher = self.session.query(Teacher).filter_by(id=data.id).first()
        if not teacher:
            return None
        try:
            data.update_time = get_current_datetime_str()
            copy_properties(data, teacher)
            self.session.commit()
            return teacher
        except Exception as e:
            print(repr(e))
            self.session.rollback()
            raise SqlError

    def delete_teacher(self, primary: int):
        teacher = self.get_teacher_by_primary(primary)
        if teacher:
            try:
                self.session.delete(teacher)
                self.session.commit()
            except Exception as e:
                print(repr(e))
                self.session.rollback()
                raise SqlError


class ConfigDB:
    session: Session

    def __init__(self, session: Session):
        self.session = session

    def get_config(self):
        return self.session.query(Config).first()

    def update_config(self, data):
        config = self.session.query(Config).first()
        try:
            if config:
                copy_properties(data, config)
                self.session.commit()
                return config
            else:
                self.session.add(data)
                self.session.commit()
        except Exception as e:
            print(repr(e))
            self.session.rollback()
            raise SqlError
