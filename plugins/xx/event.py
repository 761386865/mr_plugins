import logging
from typing import Dict, Any

from mbot.core.plugins import plugin, PluginMeta, PluginContext
from plugins.xx.api import get_crawler, download_once
from plugins.xx.download_client import DownloadClient
from plugins.xx.notify import Notify
from plugins.xx.site import Site
from plugins.xx.orm import ConfigDB, DB, CourseDB, TeacherDB

_LOGGER = logging.getLogger(__name__)

db = DB()
config_db = ConfigDB(db.session)
course_db = CourseDB(db.session)
teacher_db = TeacherDB(db.session)


@plugin.after_setup
def after_setup(plugin_meta: PluginMeta, config: Dict[str, Any]):
    pass


@plugin.on_event(bind_event=['SiteListComplete'], order=1)
def on_site_list_complete(ctx: PluginContext, event_type: str, data: Dict):
    course_list = course_db.list_course(status=1)
    config = config_db.get_config()
    site = Site(config)
    client = DownloadClient(config)
    notify = Notify(config)
    if course_list:
        for course in course_list:
            torrent = site.get_local_torrent(course.code)
            if torrent:
                download_status = client.download_from_url(torrent.download_url, config.download_path, config.category)
                if download_status:
                    course.status = 2
                    course_db.update_course(course)
                    notify.push_downloading(course)


@plugin.task('sync_new_course', '同步教师的新课程', cron_expression='0 8 * * *')
def sync_new_course():
    teachers = teacher_db.list_teacher()
    library, bus = get_crawler()
    config = config_db.get_config()
    notify = Notify(config)
    if teachers:
        for teacher in teachers:
            course_code_list = bus.crawling_teacher_courses(teacher.code, teacher.limit_date)
            if course_code_list:
                for code in course_code_list:
                    row = course_db.get_course_by_code(code)
                    if row and row.status == 0:
                        row.status = 1
                        row.sub_type = 2
                        course_db.update_course(row)
                        notify.push_new_course(teacher=teacher, course=row)
                        download_once(row)

                    else:
                        course = bus.search_code(code)
                        if course:
                            course.status = 1
                            course.sub_type = 2
                            course = course_db.add_course(course)
                            notify.push_new_course(teacher=teacher, course=row)
                            download_once(course)

