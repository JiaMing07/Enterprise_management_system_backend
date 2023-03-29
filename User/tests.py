import random
from django.test import TestCase, Client
from User.models import User
from Department.models import Department, Entity
import hashlib

# Create your tests here.
class UserTests(TestCase):
    def test_for_unit(self):
        self.assertNotEqual(0, 1)
    
    # Initializer
    def setUp(self):
        ent = Entity.objects.create(id=1, name='ent')
        dep = Department.objects.create(id=1, name='dep', entity=ent)
        password='123'
        md5 = hashlib.md5()
        md5.update(password.encode('utf-8'))
        pwd = md5.hexdigest()
        print(pwd)
        User.objects.create(username='Alice', password=pwd, department=dep, entity=ent)

    # Utility functions
    def post_user_login_normal(self, username, password):
        payload = {
            'username': username,
            'password': password
        }

        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.post("/user/login/normal", data=payload, content_type="application/json")
    
    def post_user_login_feishu(self, username_feishu, password_feishu):
        payload = {
            'username_feishu': username_feishu,
            'password_feishu': password_feishu
        }

        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.post("/user/login/feishu", data=payload, content_type="application/json")
    
    def post_user_logout_normal(self, username):
        payload = {
            'username': username
        }

        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.post("/user/logout/normal", data=payload, content_type="application/json")
    
    def post_user_add(self, name, entity, department, authority, password):
        payload = {
            'name': name,
            'entity': entity,
            'department': department,
            'authority': authority,
            'password': password
        }

        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.post("/user/add", data=payload, content_type="application/json")
    
    def post_user_list(self, entity):
        payload = {
            'entity': entity
        }

        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.post("/user/list", data=payload, content_type="application/json")
    
    def post_user_edit(self, username, password, department, authority):
        payload = {
            'username': username,
            'password': password,
            'department': department,
            'authority': authority
        }

        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.post("/user/edit", data=payload, content_type="application/json")
    
    def post_user_lock(self, username, active):
        payload = {
            'username': username,
            'active': active
        }

        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.post("/user/lock", data=payload, content_type="application/json")
    
    def get_user_username(self, username):
        return self.client.get(f"/user/{username}")
    
    def get_user_assets_username(self, username):
        return self.client.get(f"/user/assets/{username}")
    
    def get_user_list(self):
        return self.client.get(f"/user/list")
    
    # Now start testcases. 

    # Repeat the login
    def test_user_login_normal(self):
        username = 'Bob'
        password = '456'
        res = self.post_user_login_normal(username, password)

        self.assertEqual(res.json()['code'], 2)

        username = 'Alice'
        password = '123'
        res = self.post_user_login_normal(username, password)
        print(res.json()['info'])
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')
        
        res = self.post_user_login_normal(username, password)

        self.assertEqual(res.json()['code'], 1)

    # login and logout
    def test_user_logout_normal(self):
        username = 'Alice'
        password = '123'
        res = self.post_user_login_normal(username, password)

        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')

        res = self.post_user_logout_normal(username)

        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')

        res = self.post_user_login_normal(username, password)

        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')

    def test_user_add(self):
        username = 'Bob'
        # entity not found
        entity = 'en'
        department = 'dep'
        authority = 'entity_super'
        password = '456'

        res = self.post_user_add(username, entity, department, authority, password)
        self.assertEqual(res.json()['code'], 1)

        entity = 'ent'
        # department not found
        department = 'de'

        res = self.post_user_add(username, entity, department, authority, password)
        self.assertEqual(res.json()['code'], 1)

        department = 'dep'

        res = self.post_user_add(username, entity, department, authority, password)
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')

        res = self.post_user_login_normal(username, password)
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')

        # repeat the username
        password = '789'

        res = self.post_user_add(username, entity, department, authority, password)
        self.assertEqual(res.json()['code'], 1)

        # entity_super is existed
        username = 'Carol'

        res = self.post_user_add(username, entity, department, authority, password)
        self.assertEqual(res.json()['code'], 2)

        res = self.post_user_login_normal(username, password)
        self.assertEqual(res.json()['code'], 2)

    def test_user_lock(self):
        # user not found
        username = 'Bob'
        password = '123'
        active = 0

        res = self.post_user_lock(username, active)
        self.assertEqual(res.json()['code'], 1)

        # lock and repeat the lock
        username = 'Alice'

        res = self.post_user_lock(username, active)
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')

        user = User.objects.filter(username=username).first()
        self.assertFalse(user.active)

        res = self.post_user_lock(username, active)
        self.assertEqual(res.json()['code'], 2)
        
        res = self.post_user_login_normal(username, password)
        self.assertEqual(res.json()['code'], 3)

        # unlock
        active = 1

        res = self.post_user_lock(username, active)
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')

        res = self.post_user_lock(username, active)
        self.assertEqual(res.json()['code'], 2)

        user = User.objects.filter(username=username).first()
        self.assertTrue(user.active)

        res = self.post_user_login_normal(username, password)
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')

        # active error
        active = 't'
        res = self.post_user_lock(username, active)
        self.assertEqual(res.json()['code'], -2)

        active = 2
        res = self.post_user_lock(username, active)
        self.assertEqual(res.json()['code'], -2)

        user = User.objects.filter(username=username).first()
        self.assertTrue(user.active)

    def test_get_user_list(self):
        res = self.get_user_list()
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.status_code, 200)