from django.apps import AppConfig
from django.db.utils import IntegrityError, OperationalError

def init_entity():
    from Department.models import Entity

    if not Entity.objects.all().exists():
        admin_entity = Entity(name='admin_entity')
        admin_entity.save()

def init_department():
    from Department.models import Department, Entity

    if not Department.objects.all().exists():
        if not Entity.objects.all().exists():
            admin_entity = Entity(name='admin_entity')
            admin_entity.save()
        else:
            admin_entity = Entity.objects.filter(name='admin_entity').first()
        admin_department = Department(name='admin_department', entity=admin_entity, parent=None)
        admin_department.save()

def admin_user():
    from Department.models import Department, Entity
    from .models import User
    if not User.objects.filter(username='admin').exists():
        password = 'admin'
        admin = User(username='admin', password=password, department=Department.root(), entity=Entity.objects.filter(name='admin_entity').first(), system_super=True)
        admin.save()

def add_users():
    from Department.models import Department, Entity
    from .models import User
    if not Entity.objects.filter(name='entity_1').exists():
        entity = Entity(name='entity_1')
        entity.save()
    else:
        entity = Entity.objects.filter(name='entity_1').first()
    if not Department.objects.filter(name='entity_1').exists():
        department = Department(name='entity_1', parent=Department.root(), entity=entity)
    else:
        department = Department.objects.filter(name='entity_1').first()
    if not User.objects.filter(name='Alice'):
        password='123'
        user_1 = User(username='Alice', password=password, department=department, entity=entity)
        user_1.save()
    if not User.objects.filter(name='Bob'):
        password='456'
        user_2 =  User(username='Alice', password=password, department=department, entity=entity)
        user_2.save()

class UserConfig(AppConfig):
    name = 'User'

    def ready(self):
        super().ready()
        try:  # 在数据表创建前调用会引发错误
            init_entity()
            init_department()
            admin_user()
        except (OperationalError, IntegrityError):
            pass
