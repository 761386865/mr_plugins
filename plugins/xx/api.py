from flask import Blueprint, request, Flask, render_template

from plugins.xx.utils import *
from plugins.xx.crawler import JavLibrary, JavBus, TopRankNotFundError, JavBusPageError
from plugins.xx.models import Result, Course, Teacher
from plugins.xx.orm import DB, CourseDB, TeacherDB

bp = Blueprint('api', __name__)
app = Flask(__name__)
db = DB()
course_db = CourseDB(db.session)
teacher_db = TeacherDB(db.session)
proxies = {
    'https': 'http://127.0.0.1:7890'
}
library = JavLibrary(
    ua='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.61',
    cookie='timezone=-480; __qca=P0-560311510-1671015484571; over18=18; __cf_bm=h2.iWK7gRG1DgUAsymrmzI.Y7scFYNwnRrusxOZcep8-1674363571-0-AUCk98DnfNv1eoTI1SMzbMf7+mG6Ee7pdK4caLJ4WHCCLAKIpi7G6Ox0ifVwJJnGmpfWBmcYomFir+aWIMcVuC6ktoh60L0Ltw9l986L0ftn7GxzfxWP8Mf5CjQn8Yn6Qtyd3oXAk9IxqMhsxpo/UEY=',
    proxies=proxies)
bus = JavBus(cookie='PHPSESSID=j6l9m1ucqhedq3630vcj3fcso3; existmag=all', proxies=proxies)


@app.after_request
def change_header(response):
    disposition = response.get_wsgi_headers('environ').get(
        'Content-Disposition') or ''
    if disposition.rfind('.js') == len(disposition) - 3:
        response.mimetype = 'application/javascript'
    return response


@bp.route('/xx', methods=["GET"])
def index():
    return render_template('index.html')


@bp.route('/api/course/list', methods=["GET"])
def list_course():
    keyword = request.args.get('keyword')
    status = request.args.get('status')
    if status:
        status = int(status)
    courses = course_db.filter_course(keyword, status)
    dict_arr = [obj_trans_dict(course) for course in courses]
    return Result.success(dict_arr)


@bp.route('/api/teacher/list', methods=["GET"])
def list_teacher():
    keyword = request.args.get('keyword')
    teachers = teacher_db.filter_teacher(keyword)
    dict_arr = []
    for teacher in teachers:
        teacher_dict = obj_trans_dict(teacher)
        teacher_dict['status'] = 1
        dict_arr.append(teacher_dict)
    return Result.success(dict_arr)


@bp.route('/api/course/delete', methods=["GET"])
def delete_course():
    course_id = request.args.get('id')
    try:
        course_db.delete_course(int(course_id))
        return Result.success(None)
    except Exception as e:
        print(str(e))
        return Result.fail("删除失败")


@bp.route('/api/teacher/delete', methods=["GET"])
def delete_teacher():
    teacher_id = request.args.get('id')
    try:
        teacher_db.delete_teacher(int(teacher_id))
        return Result.success(None)
    except Exception as e:
        print(str(e))
        return Result.fail("删除失败")


@bp.route('/api/course/add', methods=["POST"])
def add_course():
    data = request.json
    course = Course(data)
    course.status = 1
    course.sub_type = 1
    row = course_db.get_course_by_code(course.code)
    if row:
        return Result.success(None)
    try:
        course_db.add_course(course)
    except Exception as e:
        print(str(e))
        return Result.fail("订阅失败")
    return Result.success(None)


@bp.route('/api/teacher/add', methods=["POST"])
def add_teacher():
    data = request.json
    teacher = Teacher(data)
    row = teacher_db.get_teacher_by_code(teacher.code)
    if row:
        return Result.success(None)
    try:
        teacher_db.add_teacher(teacher)
    except Exception as e:
        print(str(e))
        return Result.fail("订阅失败")
    return Result.success(None)


@bp.route('/api/rank/list', methods=["GET"])
def list_rank():
    try:
        top20_codes = library.crawling_top20()
        top20_course = []
        for code in top20_codes:
            course = course_db.get_course_by_code(code)
            if course:
                top20_course.append(obj_trans_dict(course))
            else:
                course = bus.search_code(code)
                if course:
                    course.status = 0
                    top20_course.append(obj_trans_dict(course))
        return Result.success(top20_course)
    except TopRankNotFundError:
        return Result.fail("获取榜单失败")
    except JavBusPageError:
        return Result.fail("获取课程信息失败")
    except Exception as e:
        print(repr(e))
        return Result.fail("服务器异常,检查日志")


@bp.route('/api/complex/search', methods=["GET"])
def search():
    keyword = request.args.get('keyword')
    result_list = []
    if not keyword:
        return Result.fail("请输入关键字")
    try:
        if len(keyword) == len(keyword.encode()) and has_number(keyword):
            true_code = get_true_code(keyword)
            row = course_db.get_course_by_code(true_code)
            if row:
                course_dict = obj_trans_dict(row)
                course_dict['type'] = 'course'
                result_list.append(course_dict)
            else:
                course = bus.search_code(true_code)
                if course:
                    course_dict = obj_trans_dict(course)
                    course_dict['status'] = 0
                    course_dict['type'] = 'course'
                    result_list.append(course_dict)

            teacher_code_list = bus.get_teachers(true_code)
            set_teacher(teacher_code_list, result_list)
        else:
            teacher_code_list = bus.search_all_by_name(keyword)
            set_teacher(teacher_code_list, result_list)
        return Result.success(result_list)
    except JavBusPageError:
        return Result.fail("获取课程信息失败")
    # except Exception as e:
    #     print(repr(e))
    #     return Result.fail("服务器异常,检查日志")


def set_teacher(teacher_code_list: [], result_list: []):
    if teacher_code_list:
        for teacher_code in teacher_code_list:
            row = teacher_db.get_teacher_by_code(teacher_code)
            if row:
                teacher_dict = obj_trans_dict(row)
                teacher_dict['status'] = 1
                teacher_dict['type'] = 'teacher'
                result_list.append(teacher_dict)
            else:
                teacher = bus.crawling_teacher(teacher_code)
                if teacher:
                    teacher_dict = obj_trans_dict(teacher)
                    teacher_dict['status'] = 0
                    teacher_dict['type'] = 'teacher'
                    result_list.append(teacher_dict)


if __name__ == '__main__':
    app.register_blueprint(bp)
    app.run()
