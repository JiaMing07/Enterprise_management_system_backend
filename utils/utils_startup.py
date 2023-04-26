import hashlib
from .utils_time import get_timestamp

base_menu = [{
	"first":"用户管理",
	"second":"",
	"url":"/user_manage",
	"authority":"entity_super"
},
{
	"first":"组织管理",
	"second":"",
	"url":"/group_manage",
	"authority":"entity_super"
},
{
	"first":"资产管理",
	"second":"资产录入",
	"url":"/asset_add",
	"authority":"entity_super/asset_super"
},
{
	"first":"资产管理",
	"second":"部门资产管理",
	"url":"/asset_manage",
	"authority":"entity_super/asset_super"
},
{
	"first":"资产使用",
	"second":"资产领用",
	"url":"/asset_user_require",
	"authority":"staff"
},
{
	"first":"资产管理",
	"second":"资产查看",
	"url":"/asset_manage_user",
	"authority":"staff"
},
{
	"first":"资产使用",
	"second":"请求审批",
	"url":"/request_approve",
	"authority":"asset_super"
},
{
	"first":"资产使用",
	"second":"请求列表",
	"url":"/request_list",
	"authority":"asset_super"
},
{
	"first":"资产使用",
	"second":"用户请求",
	"url":"/request_user",
	"authority":"staff"
},
{
	"first":"资产管理员首页",
	"second":"",
	"url":"/asset_super",
	"authority":"asset_super"
},
{
	"first":"系统管理员首页",
	"second":"",
	"url":"/entity_super",
	"authority":"entity_super"
},
{
	"first":"资产标签",
	"second":"添加标签",
	"url":"/asset_label",
	"authority":"asset_super"
},
{
	"first":"资产标签",
	"second":"使用标签",
	"url":"/asset_label_list",
	"authority":"staff/asset_super"
},
]

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
    for menu in base_menu:
        if not Menu.objects.filter(first=menu['first'], second=menu['second']).exists():
            menu_1 = Menu(first=menu['first'], second=menu['second'], url=menu['url'])
            au = menu['authority'].split('/')
            menu_1.entity_show, menu_1.asset_show, menu_1.staff_show = menu_1.set_authority(au)
            menu_1.entity = Entity.objects.filter(name="admin_entity").first()
            menu_1.save()

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
        category_1.save()

def add_request():
    from User.models import User
    from Department.models import Entity, Department
    from Asset.models import AssetCategory, Asset
    from Request.models import NormalRequests, TransferRequests
    entity=Entity.objects.filter(name="entity_1").first()
    department = Department.objects.filter(name='department_1', entity=entity).first()
    if not User.objects.filter(username="David").exists():
        password='123'
        md5 = hashlib.md5()
        md5.update(password.encode('utf-8'))
        password = md5.hexdigest()
        user_1 = User(username='David', password=password, department=department, entity=entity)
        user_1.save()
    user_1 = User.objects.filter(username='David').first()
    if not Asset.objects.filter(name="test_request_asset_1").exists():
        asset_1 = Asset(name="test_request_asset_1",entity=entity, category=AssetCategory.objects.filter(name="category_base").first(), department=department)
        asset_1.save()
        request_1 = NormalRequests(initiator=user_1, asset=asset_1, type=1, result=0, request_time=get_timestamp(),review_time=0.0)
        request_1.save()
    if not Asset.objects.filter(name="test_request_asset_2").exists():
        asset_2 = Asset(name="test_request_asset_2",entity=entity, category=AssetCategory.objects.filter(name="category_base").first(), department=department)
        asset_2.save()
        request_2 = NormalRequests(initiator=user_1, asset=asset_2, type=2, result=0, request_time=get_timestamp(),review_time=0.0)
        request_2.save()
    if not Asset.objects.filter(name="test_request_asset_3").exists():
        asset_3 = Asset(name="test_request_asset_3",entity=entity, category=AssetCategory.objects.filter(name="category_base").first(), department=department)
        asset_3.save()
        request_3 = NormalRequests(initiator=user_1, asset=asset_3, type=3, result=0, request_time=get_timestamp(),review_time=0.0)
        request_3.save()
    if not Asset.objects.filter(name="test_request_asset_4").exists():
        asset_4 = Asset(name="test_request_asset_4",entity=entity, category=AssetCategory.objects.filter(name="category_base").first(), department=department)
        asset_4.save()
        participant = User.objects.filter(username="Alice").first()
        pos = "pos1"
        request_4 = TransferRequests(initiator=user_1, participant=participant, asset=asset_4, type=4, result=0, request_time=get_timestamp(),review_time=0.0, position=pos)
        request_4.save()