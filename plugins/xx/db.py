from plugins.xx.orm import DB, CourseDB, TeacherDB, ConfigDB

db = DB()

course_db = CourseDB(db.session)
teacher_db = TeacherDB(db.session)
config_db = ConfigDB(db.session)






def get_course_db() -> CourseDB:
    return course_db


def get_teacher_db() -> TeacherDB:
    return teacher_db


def get_config_db() -> ConfigDB:
    return config_db
