from plugins.xx.base_config import get_base_config, ConfigType
from plugins.xx.models import Config, Course, Teacher
from mbot.openapi import mbot_api


class Notify:
    config: Config

    def __init__(self, config: Config):
        self.config = config

    @staticmethod
    def is_telegram(channel_name):
        channel_configs = get_base_config(ConfigType.Notify_Channel)
        channel_list = list(filter(lambda x: x['name'] == channel_name, channel_configs))
        if not channel_list:
            return False
        if channel_list[0]['type'] == 'telegram':
            return True

    def push_subscribe_course(self, course: Course):
        if not self.config.msg_uid:
            return False
        if not self.config.msg_channel:
            return False
        uid_list = self.config.msg_uid.split(',')
        channel_list = self.config.msg_channel.split(',')
        context = {
            'is_aired': True,
            'release_date': course.release_date,
            'nickname': '不愿透露名字',
            'country': ['霓虹'],
            'cn_name': course.code,
            'pic_url': self.config.msg_img
        }
        for uid in uid_list:
            for channel in channel_list:
                if self.is_telegram(channel):
                    context['genres'] = course.genres.split(',')
                    context['intro'] = course.title
                mbot_api.notify.send_message_by_tmpl_name('sub_movie', context=context, to_uid=int(uid),
                                                          to_channel_name=channel)

    def push_new_course(self, teacher: Teacher, course: Course):
        if not self.config.msg_uid:
            return False
        if not self.config.msg_channel:
            return False
        uid_list = self.config.msg_uid.split(',')
        channel_list = self.config.msg_channel.split(',')
        context = {
            'is_aired': True,
            'release_date': course.release_date,
            'nickname': teacher.name,
            'country': ['霓虹'],
            'cn_name': course.code,
            'pic_url': self.config.msg_img
        }
        for uid in uid_list:
            for channel in channel_list:
                if self.is_telegram(channel):
                    context['genres'] = course.genres.split(',')
                    context['intro'] = course.title
                mbot_api.notify.send_message_by_tmpl_name('sub_movie', context=context, to_uid=int(uid),
                                                          to_channel_name=channel)

    def push_subscribe_teacher(self, teacher: Teacher):
        if not self.config.msg_uid:
            return False
        if not self.config.msg_channel:
            return False
        uid_list = self.config.msg_uid.split(',')
        channel_list = self.config.msg_channel.split(',')
        title = f"🍿订阅: {teacher.name}老师"
        body = "于{{limit_date}}开始任教\n" \
               "··········································\n" \
               "{% if birth %} · {{birth}}{% endif %}" \
               "{% if height %} · {{height}}{% endif %}" \
               "{% if cup %} · {{cup}}{% endif %}" \
               "{% if bust %} · {{bust}}{% endif %}" \
               "{% if waist %} · {{waist}}{% endif %}" \
               "{% if hip %} · {{hip}}{% endif %}"
        context = {
            'name': teacher.name,
            'birth': teacher.birth,
            'height': teacher.height,
            'cup': teacher.cup,
            'bust': teacher.bust,
            'waist': teacher.waist,
            'hip': teacher.hip,
            'limit_date': teacher.limit_date,
            'pic_url': self.config.msg_img
        }
        for uid in uid_list:
            mbot_api.notify.send_message_by_tmpl(title=title, body=body, context=context,
                                                 to_uid=int(uid),
                                                 to_channel_name=channel_list)

    def push_downloading(self, course: Course):
        if not self.config.msg_uid:
            return False
        if not self.config.msg_channel:
            return False
        uid_list = self.config.msg_uid.split(',')
        channel_list = self.config.msg_channel.split(',')
        context = {
            'year': course.release_date[0:3],
            'nickname': '不愿透露名字',
            'title': f"下载: {course.code}",
            'pic_url': self.config.msg_img,
            'intro': f'由{course.casts}教授的课程开始下载了'
        }
        for uid in uid_list:
            for channel in channel_list:
                if self.is_telegram(channel):
                    context['intro'] = course.title
                mbot_api.notify.send_message_by_tmpl_name('download_start_movie', context=context, to_uid=int(uid),
                                                          to_channel_name=channel)
