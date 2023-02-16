import logging

from plugins.xx.models import Config, Course, Teacher

_LOGGER = logging.getLogger(__name__)


class Notify:
    config: Config

    def __init__(self, config: Config):
        self.config = config

    def push_subscribe_course(self, course: Course):
        pass

    def push_new_course(self, teacher: Teacher, course: Course):
        pass

    def push_subscribe_teacher(self, teacher: Teacher):
        pass

    def push_downloading(self, course: Course):
        pass
