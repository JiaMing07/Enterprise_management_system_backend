import hashlib

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
    from User.models import User
    if not User.objects.filter(username='admin').exists():
        password = 'admin'
        md5 = hashlib.md5()
        md5.update(password.encode('utf-8'))
        password = md5.hexdigest()
        admin = User(username='admin', password=password, department=Department.root(), entity=Entity.objects.filter(name='admin_entity').first(), system_super=True)
        admin.save()

def add_users():
    from Department.models import Department, Entity
    from User.models import User
    if not Entity.objects.filter(name='entity_1').exists():
        entity = Entity(name='entity_1')
        entity.save()
    else:
        entity = Entity.objects.filter(name='entity_1').first()
    if not Department.objects.filter(entity=entity).filter(name='department_1').exists():
        parent = Department.objects.filter(name='entity_1').first()
        if not parent:
            parent = Department(name='entity_1', parent=Department.root(), entity=entity)
            parent.save()
        department = Department(name='department_1', parent=parent, entity=entity)
        department.save()
    else:
        department = Department.objects.filter(name='entity_1').first()
    if not User.objects.filter(username='Alice'):
        password='123'
        md5 = hashlib.md5()
        md5.update(password.encode('utf-8'))
        password = md5.hexdigest()
        user_1 = User(username='Alice', password=password, department=department, entity=entity)
        user_1.save()
    if not User.objects.filter(username='Bob'):
        password='456'
        md5 = hashlib.md5()
        md5.update(password.encode('utf-8'))
        password = md5.hexdigest()
        user_2 =  User(username='Bob', password=password, department=department, entity=entity)
        user_2.save()

def add_menu():
    from Department.models import Department, Entity
    from User.models import User, Menu
    if not Menu.objects.filter(first='首页').filter(second='').exists():
        menu_1 = Menu(first="首页",second="",url="https://eam-frontend-bughunters.app.secoder.net/super_manager", entity_show = True, asset_show=True, staff_show=True)
        menu_1.entity = Entity.objects.filter(name="admin_entity").first()
        menu_1.save()
    if not Menu.objects.filter(first='用户管理').filter(second='').exists():
        menu_2 = Menu(first="用户管理",second="",url="https://eam-frontend-bughunters.app.secoder.net/user_manage", entity_show=True)
        menu_2.entity = Entity.objects.filter(name="admin_entity").first()
        menu_2.save()
    if not Menu.objects.filter(first='资产管理').filter(second='').exists():
        menu_3 = Menu(first="资产管理", second="", url="https://eam-frontend-bughunters.app.secoder.net",asset_show=True)
        menu_3.entity = Entity.objects.filter(name="admin_entity").first()
        menu_3.save()
    if not Menu.objects.filter(first='查看事项').filter(second='审批情况').exists():
        menu_4 = Menu(first="查看事项", second="审批情况", url="https://eam-frontend-bughunters.app.secoder.net/asset",staff_show=True)
        menu_4.entity = Entity.objects.filter(name="admin_entity").first()
        menu_4.save()

def add_category():
    from Department.models import Entity
    from Asset.models import AssetCategory

    entity=Entity.objects.filter(name="admin_entity").first()
    if not AssetCategory.objects.filter(name="category_base").exists():
        category_1 = AssetCategory(name="category_base",entity=entity, is_number=False)
        category_1.save()
    entity=Entity.objects.filter(name="entity_1").first()
    if not AssetCategory.objects.filter(name="entity_1").exists():
        category_2 = AssetCategory(name="entity_1", parent=AssetCategory.objects.filter(name="category_base").first(), entity=entity, is_number=True)
        category_2.save()
    if not AssetCategory.objects.filter(name="category_1_en1").exists():
        category_3 = AssetCategory(name="category_1_en1",parent=AssetCategory.objects.filter(name="entity_1").first(), entity=Entity.objects.filter(name="entity_1").first(), is_number=False)
        category_3.save()

def add_asset():
    from Department.models import Entity, Department
    from Asset.models import AssetCategory, Asset
    entity=Entity.objects.filter(name="admin_entity").first()
    if not Asset.objects.filter(name="asset_base").exists():
        category_1 = Asset(name="asset_base",entity=entity, category=AssetCategory.objects.filter(name="category_base").first(), department=Department.objects.filter(name="admin_department").first())
        print(category_1)
        category_1.save()