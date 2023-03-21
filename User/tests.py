import random
from django.test import TestCase, Client
from User.models import User
from Department.models import Department, Entity

# Create your tests here.
class UserTests(TestCase):
    def test_for_unit(self):
        self.assertNotEqual(0, 1)
    
    def setUp(self):
        ent = Entity.objects.create(id=1, name='en')
        dep = Department.objects.create(id=1, name='dep', entity=ent)
        User.objects.create(username='Alice', password='123', department=dep, entity=ent)

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
    
    def post_user_logout(self, username):
        payload = {
            'username': username
        }

        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.post("/user/logout", data=payload, content_type="application/json")
    
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
    
    def test_login_normal(self):
        username = 'Alice'
        password = '456'
        res = self.post_user_login_normal(username, password)

        self.assertEqual(res.json()['code'], 2)

        password = '123'
        res = self.post_user_login_normal(username, password)

        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')
        
        res = self.post_user_login_normal(username, password)

        self.assertEqual(res.json()['code'], 1)
