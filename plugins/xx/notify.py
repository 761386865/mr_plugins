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
        channel_list = list(filter(lambda x: x.name == channel_name, channel_configs))
        if not channel_list:
            return False
        if channel_list[0]['type'] == 'telegram':
            return True

    def push_subscribe_course(self, course: Course):
        uid_list = self.config.msg_uid.split(',')
        channel_list = self.config.msg_channel.split(',')
        context = {
            'is_aired': True,
            'release_date': course.release_date,
            'nickname': '不愿透露名字',
            'country': '日本',
            'genres': course.genres,
            'intro': course.title,
            'title': course.code,
            'pic_url': self.config.msg_img
        }

        for uid in uid_list:
            for channel in channel_list:
                if self.is_telegram(channel):
                    context['pic_url'] = f'https://www.javbus.com{course.banner}'
                mbot_api.notify.send_message_by_tmpl_name('sub_movie', context=context, to_uid=int(uid),
                                                          to_channel_name=channel_list)

        pass

    def push_new_course(self, teacher: Teacher, course: Course):
        uid_list = self.config.msg_uid.split(',')
        channel_list = self.config.msg_channel.split(',')
        context = {
            'is_aired': True,
            'release_date': course.release_date,
            'nickname': teacher.name,
            'country': '日本',
            'genres': course.genres,
            'intro': course.title,
            'title': course.code,
            'pic_url': self.config.msg_img
        }
        for uid in uid_list:
            for channel in channel_list:
                if self.is_telegram(channel):
                    context['pic_url'] = f'https://www.javbus.com{course.banner}'
                mbot_api.notify.send_message_by_tmpl_name('sub_movie', context=context, to_uid=int(uid),
                                                          to_channel_name=channel_list)

    def push_subscribe_teacher(self, teacher: Teacher):
        uid_list = self.config.msg_uid.split(',')
        channel_list = self.config.msg_channel.split(',')
        title = f"订阅老师:{teacher.name}"
        body = "{% if birth %}生日:{{birth}}\n{% endif %}" \
               "{% if height %}身高:{{height}}\n{% endif %}" \
               "{% if cup %}罩杯:{{cup}}\n{% endif %}" \
               "{% if bust %}胸围:{{bust}}\n{% endif %}" \
               "{% if waist %}腰围:{{waist}}\n{% endif %}" \
               "{% if hip %}臀围:{{hip}}\n{% endif %}" \
               "{% if limit_date %}限制日期:{{limit_date}}{% endif %}"
        context = {
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
        uid_list = self.config.msg_uid.split(',')
        channel_list = self.config.msg_channel.split(',')
        context = {
            'year': course.release_date[0:3],
            'nickname': '不愿透露名字',
            'title': course.code,
            'file_size': course.title,
            'pic_url': self.config.msg_img
        }
        for uid in uid_list:
            for channel in channel_list:
                if self.is_telegram(channel):
                    context['pic_url'] = f'https://www.javbus.com{course.banner}'
                mbot_api.notify.send_message_by_tmpl_name('download_start_movie', context=context, to_uid=int(uid),
                                                          to_channel_name=channel_list)
