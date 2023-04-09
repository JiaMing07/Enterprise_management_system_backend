from django.apps import AppConfig
from django.db.utils import IntegrityError, OperationalError
import hashlib


class UserConfig(AppConfig):
    name = 'User'

    # def ready(self):
    #     # super().ready()
    #     try:  # 在数据表创建前调用会引发错误
    #         init_entity()
    #         init_department()
    #         admin_user()
    #         add_users()
    #         add_menu()
    #     except (OperationalError, IntegrityError):
    #         pass
