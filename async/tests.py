from django.test import *
from Asset.models import *
from Department.models import *
from User.models import *
import hashlib
from http import cookies
import time
import asyncio
from asgiref.sync import sync_to_async

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
        user = User.objects.create(username='test_user', password=pwd, department=dep, entity=ent)
        category = AssetCategory.objects.create(name='cate', entity=ent)
        Asset.objects.create(name='ass', entity=ent, owner=user.username, category=category, department=dep)
        Attribute.objects.create(id=1, name="attri_0", entity=ent, department=dep_ent)

    async def create_token(self, name, authority):
        user = await User.objects.filter(username=name).afirst()
        user.token = user.generate_token()
        user.system_super, user.entity_super, user.asset_super = user.set_authen(authority)
        await user.asave()
        Token = user.token
        c = cookies.SimpleCookie()
        c['token'] = Token
        self.client.cookies = c
        self.async_client.cookies = c
    
    async def post_async_add(self, body):
        payload = {
            'assets': body
        }
        payload = {k: v for k, v in payload.items() if v is not None}
        res = await self.async_client.post("/async/add", data=payload, content_type="application/json")
        return res
        
    async def post_async_restart(self, id):
        payload = {
            'id': id
        }
        payload = {k: v for k, v in payload.items() if v is not None}
        res = await self.async_client.post("/async/restart", data=payload, content_type="application/json")
        return res
    
    def get_async_list(self):
        return self.client.get('/async/list')
    
    def get_failed_list(self):
        return self.client.get('/async/failed')
    
    async def test_async_add(self):
        user = await User.objects.filter(username='test_user').afirst()
        user.token = user.generate_token()
        user.system_super, user.entity_super, user.asset_super = user.set_authen('staff')
        await user.asave()
        Token = user.token
        c = cookies.SimpleCookie()
        c['token'] = Token
        self.client.cookies = c
        self.async_client.cookies = c

        assets = [
            {
            "name": 'computer', 
            "parent": '', 
            "description": 'work', 
            "position": 'desk', 
            "value": 5999, 
            "department": 'dep_child',
            "number": 1, 
            "category": 'cate',
            "life": 5,
            "image": '127.0.0.1',
            },
            {
            "name": 'keyboard', 
            "parent": 'computer', 
            "description": 'work', 
            "position": 'desk', 
            "value": 100, 
            "department": '',
            "number": 1, 
            "category": 'cate',
            "life": 5,
            "image": '127.0.0.2',
            "state": 'IN_USE',
            "owner": 'Alice',
            },
            {
            "name": 'keyboard', 
            "parent": 'asset_1', #parent not found
            "description": 'work', 
            "position": 'desk', 
            "value": 100, 
            "department": '',
            "number": 1, 
            "category": 'cate',
            "life": 5,
            "image": '127.0.0.2',
            },
            {
            "name": 'keyboard', 
            "parent": 'computer', 
            "description": 'work', 
            "position": 'desk', 
            "value": 100, 
            "department": 'department_1',# department not found
            "number": 1, 
            "category": 'cate',
            "life": 5,
            "image": '127.0.0.2',
            },
            {
            "name": 'keyboard', 
            "parent": 'computer', 
            "description": 'work', 
            "position": 'desk', 
            "value": 100, 
            "department": 'dep_child',
            "number": 1, 
            "category": 'category_1',# category not found
            "life": 5,
            "image": '127.0.0.2',
            },
            {
            "name": 'keyboard',# repeat
            "parent": 'computer', 
            "description": 'work', 
            "position": 'desk', 
            "value": 100, 
            "department": 'dep_child',
            "number": 1, 
            "category": 'cate',
            "life": 5,
            "image": '127.0.0.2',
            },
            {
            "name": 'mouse', 
            "parent": 'computer', 
            "description": 'work', 
            "position": 'desk', 
            "value": 100, 
            "department": 'dep_child',
            "number": 1, 
            "category": 'cate',
            "life": 5,
            "image": '127.0.0.3',
            "owner": 'Bob',# owner not found
            },
            {
            "name": 'mouse', 
            "parent": 'computer', 
            "description": 'work', 
            "position": 'desk', 
            "value": 100, 
            "department": 'dep',# 部门不在管理范围内
            "number": 1, 
            "category": 'cate',
            "life": 5,
            "image": '127.0.0.3',
            }
        ]
        
        res = await self.post_async_add(assets)
        print(res)
        self.assertEqual(res.json()['info'], '没有操作权限')

        await self.create_token('test_user', 'entity_super')
        res = await self.post_async_add(assets)
        self.assertEqual(res.json()['info'], 'Succeed')

        res = await self.post_async_restart(0)
        self.assertEqual(res.json()['info'], '请求体错误，不存在对应原始任务')
        
        res = await self.post_async_restart(3)
        self.assertEqual(res.json()['info'], '不存在原始任务')

        res = await self.post_async_restart(1)
        self.assertEqual(res.json()['info'], 'Succeed')

    def test_list(self):
        user = User.objects.filter(username='test_user').first()
        user.token = user.generate_token()
        user.system_super, user.entity_super, user.asset_super = user.set_authen('entity_super')
        user.save()
        Token = user.token
        c = cookies.SimpleCookie()
        c['token'] = Token
        self.client.cookies = c

        res = self.get_async_list()
        self.assertEqual(res.json()['info'], 'Succeed')

        res = self.get_failed_list()
        self.assertEqual(res.json()['info'], 'Succeed')
