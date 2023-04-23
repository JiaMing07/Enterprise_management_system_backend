from django.test import TestCase, Client
from Asset.models import AssetCategory, Asset, Attribute, AssetAttribute
from Department.models import Department, Entity
from User.models import User, Menu
import hashlib
from http import cookies

# Create your tests here.

# Test for Attribute
class AttributeTests(TestCase):
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

    def post_request_return(self, asset_list):
        payload = {
            "assets": asset_list,
        }    
        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.post("/requests/return", data=payload, content_type="application/json")
    
    def get_request_waiting(self):
        return self.client.get("/requests/waiting")
    
    def post_request_repair(self, asset_list):
        payload = {
            "assets": asset_list,
        }    
        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.post("/requests/repair", data=payload, content_type="application/json")
    # start test

    def test_request_return(self):
        user = self.create_token('test_user', 'staff')
        asset_list = ["as"]
        res = self.post_request_return(asset_list)
        self.assertEqual(res.json()['info'], "第1条想要退库的资产不存在")
        self.assertEqual(res.json()['code'], 1)

        asset_list = ["ass"]
        res = self.post_request_return(asset_list)
        self.assertEqual(res.json()['info'], "第1条想要退库的资产不在使用中")
        self.assertEqual(res.json()['code'], 1)

        assets = Asset.objects.all()
        for ass in assets:
            ass.state = "IN_USE"
            ass.save()
        
        asset_list = ["ass"]
        res = self.post_request_return(asset_list)
        self.assertEqual(res.json()['info'], "Succeed")
        self.assertEqual(res.json()['code'], 0)

        asset_list = ["ass", "asset_1"]
        res = self.post_request_return(asset_list)
        self.assertEqual(res.json()['info'], "第1条想要退库的资产已提交退库申请")
        self.assertEqual(res.json()['code'], 1)
        
    def test_request_waiting(self):
        user = self.create_token('test_user', 'entity_super')

        res = self.get_request_waiting()
        self.assertEqual(res.json()['info'], 'Succeed')
        self.assertEqual(res.json()['code'], 0)
