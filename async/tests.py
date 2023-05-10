from django.test import TestCase, Client
from Asset.models import *
from Department.models import *
from User.models import *
import hashlib
from http import cookies

# Create your tests here.

# Test for Attribute
class AsyncTests(TestCase):
    def test_for_unit(self):
        self.assertNotEqual(0, 1)

    # Initializer
    def setUp(self):
        ent = Entity.objects.create(id=1, name='ent')
        
        dep_ent = Department.objects.create(id=1, name='ent', entity=ent)
        dep = Department.objects.create(id=2, name='dep', entity=ent)
        dep_child = Department.objects.create(id=3, name='dep_child', entity=ent, parent=dep)
        
        password='123'
        md5 = hashlib.md5()
        md5.update(password.encode('utf-8'))
        pwd = md5.hexdigest()

        User.objects.create(username='Alice', password=pwd, department=dep_child, entity=ent)
        User.objects.create(username='George', password=pwd, department=dep, entity=ent, asset_super=True)
        User.objects.create(username='test_attribute', password=pwd, department=dep, entity=ent)
        User.objects.create(username='test_user', password=pwd, department=dep, entity=ent)
        
        category = AssetCategory.objects.create(name='cate', entity=ent)
        
        Asset.objects.create(name='ass', entity=ent, owner="test_user", category=category, department=dep, state='IDLE')
        Asset.objects.create(name='asset_1', entity=ent, owner='George', category=category, department=dep_child)
        Asset.objects.create(name='asset_2', entity=ent, owner='George', category=category, department=dep_child)
        Asset.objects.create(name='asset_3', entity=ent, owner='George', category=category, department=dep_child)
        Attribute.objects.create(id=1, name="attri_0", entity=ent, department=dep_ent)

    def create_token(self, name, authority):
        user = User.objects.filter(username=name).first()
        user.token = user.generate_token()
        user.system_super, user.entity_super, user.asset_super = user.set_authen(authority)
        user.save()
        Token = user.token
        c = cookies.SimpleCookie()
        c['token'] = Token
        self.client.cookies = c
        return user