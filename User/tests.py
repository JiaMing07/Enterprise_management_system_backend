import random
from django.test import TestCase, Client
from User.models import User, Menu
from Department.models import Department, Entity
import hashlib
import datetime
import jwt
import time
from eam_backend.settings import SECRET_KEY
from http import cookies

# Create your tests here.
class UserTests(TestCase):
    def test_for_unit(self):
        self.assertNotEqual(0, 1)
    
    # Initializer
    def setUp(self):
        ent = Entity.objects.create(id=1, name='ent')
        entity = Entity.objects.create(id=2, name='admin_entity')
        dep_ent = Department.objects.create(id=1, name='ent', entity=ent)
        dep = Department.objects.create(id=2, name='dep', entity=ent)
        password='123'
        md5 = hashlib.md5()
        md5.update(password.encode('utf-8'))
        pwd = md5.hexdigest()
        User.objects.create(username='Alice', password=pwd, department=dep, entity=ent)
        User.objects.create(username='test_user', password=pwd, department=dep, entity=ent)
        Menu.objects.create(first="m1",second="",url="https://eam-frontend-bughunters.app.secoder.net/super_manager",entity = entity, entity_show = True, asset_show=True, staff_show=True)
        Menu.objects.create(first="m2",second="",url="https://eam-frontend-bughunters.app.secoder.net/user_manage", entity_show=True,entity=entity)
        Menu.objects.create(first="m3", second="", url="https://eam-frontend-bughunters.app.secoder.net",asset_show=True,entity=entity)
        Menu.objects.create(first="m4", second="s1", url="https://eam-frontend-bughunters.app.secoder.net/asset",staff_show=True, entity=entity)

    # Utility functions
    def post_user_login_normal(self, username, password):
        payload = {
            'username': username,
            'password': password
        }

        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.post("/user/login/normal", data=payload, content_type="application/json")
    
    def get_user_login_normal(self, username, password):
        payload = {
            'username': username,
            'password': password
        }

        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.get("/user/login/normal", data=payload, content_type="application/json")

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
    
    def get_user_logout_normal(self, username):
        payload = {
            'username': username
        }

        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.get("/user/logout/normal", data=payload, content_type="application/json")
    
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
    
    def get_user_add(self, name, entity, department, authority, password):
        payload = {
            'name': name,
            'entity': entity,
            'department': department,
            'authority': authority,
            'password': password
        }

        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.get("/user/add", data=payload, content_type="application/json")
    
    def post_user_list(self, entity):
        payload = {
            'entity': entity
        }

        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.post("/user/list", data=payload, content_type="application/json")
    
    def get_user_list(self, entity):
        payload = {
            'entity': entity
        }

        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.get("/user/list", data=payload, content_type="application/json")

    def post_user_edit(self, username, password, department, authority):
        payload = {
            'username': username,
            'password': password,
            'department': department,
            'authority': authority,
        }

        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.post("/user/edit", data=payload, content_type="application/json")
    
    def get_user_edit(self, username, password, department, authority):
        payload = {
            'name': username,
            'password': password,
            'department': department,
            'authority': authority,
        }

        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.get("/user/edit", data=payload, content_type="application/json")
    
    def post_user_lock(self, username, active):
        payload = {
            'username': username,
            'active': active
        }

        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.post("/user/lock", data=payload, content_type="application/json")
    
    def get_user_lock(self, username, active):
        payload = {
            'username': username,
            'active': active
        }

        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.get("/user/lock", data=payload, content_type="application/json")
    
    def get_user_username(self, username):
        return self.client.get(f"/user/{username}")
    
    def get_user_assets_username(self, username):
        return self.client.get(f"/user/assets/{username}")
    
    def get_user_list(self):
        return self.client.get(f"/user/list")
    
    def post_user_list(self):
        return self.client.post(f"/user/list")
    
    def delete_user_userName(self, userName):
        return self.client.delete(f"/user/{userName}")
    
    def get_user_menu(self):
        return self.client.get(f"/user/menu")
    
    def get_user_menu_list(self):
        return self.client.get(f"/user/menu/list")
    
    def post_user_menu(self, first, second, url, authority):
        payload = {
            'first': first,
            'second': second,
            'authority': authority,
            'url': url
        }

        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.post("/user/menu", data=payload, content_type="application/json")
    
    def delete_user_menu(self, first, second):
        payload = {
            'first': first,
            'second': second,
        }

        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.delete("/user/menu", data=payload, content_type="application/json")
    
    def get_user_department_list(self):
        return self.client.get("/user/department/list")

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
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')
        
        res = self.post_user_login_normal(username, password)

        self.assertEqual(res.json()['code'], 0)

        res = self.get_user_login_normal(username, password)

        self.assertEqual(res.json()['code'], -3)
        self.assertEqual(res.json()['info'], 'Bad method')

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

        res = self.get_user_logout_normal(username)

        self.assertEqual(res.json()['code'], -3)
        self.assertEqual(res.json()['info'], 'Bad method')

        res = self.post_user_login_normal(username, password)

        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')

    def test_user_add(self):
        user = User.objects.filter(username='test_user').first()
        user.token = user.generate_token()
        user.system_super, user.entity_super, user.asset_super = user.set_authen("system_super")
        user.save()
        Token = user.token
        c = cookies.SimpleCookie()
        c['token'] = Token
        self.client.cookies = c
        username = 'Bob'
        # entity not found
        entity = 'en'
        department = 'dep'
        authority = 'asset_super'
        password = '456'

        res = self.post_user_add(username, entity, department, authority, password)
        self.assertEqual(res.json()['code'], 1)

        entity = 'ent'
        # department not found
        user.system_super, user.entity_super, user.asset_super = user.set_authen("entity_super")
        user.save()
        department = 'de'

        res = self.post_user_add(username, entity, department, authority, password)
        self.assertEqual(res.json()['code'], 1)

        department = 'dep'

        user.system_super, user.entity_super, user.asset_super = user.set_authen("system_super")
        user.save()

        authority = 'entity_super'
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

        
        # system_super is existed test_user

        username = 'Emily'
        authority = 'system_super'

        res = self.post_user_add(username, entity, department, authority, password)
        self.assertEqual(res.json()['code'], 2)

        # asset_super
        user.system_super, user.entity_super, user.asset_super = user.set_authen("entity_super")
        user.save()
        authority = 'asset_super'

        res = self.post_user_add(username, entity, department, authority, password)
        self.assertEqual(res.json()['code'], 0)

        username = 'Fliss'

        res = self.post_user_add(username, entity, department, authority, password)
        self.assertEqual(res.json()['code'], 0)

        # Bad method
        res = self.get_user_add(username, entity, department, authority, password)

        self.assertEqual(res.json()['code'], -3)
        self.assertEqual(res.json()['info'], 'Bad method')


    def test_user_lock(self):
        user = User.objects.filter(username='test_user').first()
        user.token = user.generate_token()
        user.system_super, user.entity_super, user.asset_super = user.set_authen("entity_super")
        user.save()
        Token = user.token
        c = cookies.SimpleCookie()
        c['token'] = Token
        self.client.cookies = c
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

        #bad method
        res = self.get_user_lock(username, active)

        self.assertEqual(res.json()['code'], -3)
        self.assertEqual(res.json()['info'], 'Bad method')

    
    def test_user_edit(self):
        user = User.objects.filter(username='test_user').first()
        user.token = user.generate_token()
        user.system_super, user.entity_super, user.asset_super = user.set_authen("entity_super")
        user.save()
        Token = user.token
        c = cookies.SimpleCookie()
        c['token'] = Token
        self.client.cookies = c
        # user not found
        username = 'Bob'
        password = '123'
        department = 'dep'
        authority = 'entity_super'
        res = self.post_user_edit(username, password, department, authority)
        self.assertEqual(res.json()['code'], 1)

        user.system_super, user.entity_super, user.asset_super = user.set_authen("system_super")
        user.save()
        username = 'Bob'
        entity = 'ent'
        department = 'dep'
        authority = 'entity_super'
        password = '456'
        res = self.post_user_add(username, entity, department, authority, password)
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')

        
        # new password same, 3
        user.system_super, user.entity_super, user.asset_super = user.set_authen("entity_super")
        user.save()
        username = 'Bob'
        password = '456'
        department = 'dep'
        authority = 'entity_super'
        res = self.post_user_edit(username, password, department, authority)
        self.assertEqual(res.json()['code'], 3)

        # edit pwd success
        username = 'Bob'
        password = '789'
        department = None
        authority = None
        res = self.post_user_edit(username, password, department, authority)
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')

        # authority not correct, 1
        username = 'Bob'
        password = None
        department = None
        authority = 'Human'
        res = self.post_user_edit(username, password, department, authority)
        self.assertEqual(res.json()['code'], 1)

        username = 'Bob'
        password = None
        department = None
        authority = 'system_super'
        res = self.post_user_edit(username, password, department, authority)
        self.assertEqual(res.json()['code'], 5)

        # edit authority same 3
        user.system_super, user.entity_super, user.asset_super = user.set_authen("system_super")
        user.save()
        username = 'Bob'
        password = None
        department = None
        authority = 'entity_super'
        res = self.post_user_edit(username, password, department, authority)
        self.assertEqual(res.json()['code'], 3)

        # entity_super can only be 1
        user.system_super, user.entity_super, user.asset_super = user.set_authen("entity_super")
        user.save()
        username = 'Camellia'
        entity = 'ent'
        department = 'dep'
        authority = 'asset_super'
        password = '456'
        res = self.post_user_add(username, entity, department, authority, password)
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')

        user.system_super, user.entity_super, user.asset_super = user.set_authen("system_super")
        user.save()
        username = 'Camellia'
        password = None
        department = None
        authority = 'entity_super'
        res = self.post_user_edit(username, password, department, authority)
        self.assertEqual(res.json()['code'], 4)

        # authority success
        user.system_super, user.entity_super, user.asset_super = user.set_authen("entity_super")
        user.save()
        username = 'Bob'
        password = None
        department = None
        authority = 'staff'
        res = self.post_user_edit(username, password, department, authority)
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')

        # department not correct, 1
        username = 'Bob'
        password = None
        department = 'de'
        authority = None
        res = self.post_user_edit(username, password, department, authority)
        self.assertEqual(res.json()['code'], 1)

        # edit department same 3
        username = 'Bob'
        password = None
        department = 'ent'
        authority = None
        res = self.post_user_edit(username, password, department, authority)
        self.assertEqual(res.json()['code'], 3)

        # now we only have one dep, so test afterwards

        # edit both pwd and auth
        # fail because already have entity_super
        user.system_super, user.entity_super, user.asset_super = user.set_authen("system_super")
        user.save()
        username = 'Carol'
        entity = 'ent'
        department = 'dep'
        authority = 'entity_super'
        password = '456'
        res = self.post_user_add(username, entity, department, authority, password)
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')

        username = 'Bob'
        password = '456'
        department = None
        authority = 'entity_super'
        res = self.post_user_edit(username, password, department, authority)
        self.assertEqual(res.json()['code'], 4)
        self.assertEqual(res.json()['info'], '该企业已存在系统管理员')

        user.system_super, user.entity_super, user.asset_super = user.set_authen("entity_super")
        user.save()
        username = 'Bob'
        password = '456'
        department = None
        authority = 'asset_super'
        res = self.post_user_edit(username, password, department, authority)
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')

        # bad method
        res = self.get_user_edit(username, password, department, authority)
        self.assertEqual(res.json()['code'], -3)
        self.assertEqual(res.json()['info'], 'Bad method')

        
    def test_get_user_list(self):
        res = self.get_user_list()
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.status_code, 200)

        res = self.post_user_list()

        self.assertEqual(res.json()['code'], -3)
        self.assertEqual(res.json()['info'], 'Bad method')

    def test_delete_user_userName(self):
        user = User.objects.filter(username='test_user').first()
        user.token = user.generate_token()
        user.system_super, user.entity_super, user.asset_super = user.set_authen("entity_super")
        user.save()
        Token = user.token
        c = cookies.SimpleCookie()
        c['token'] = Token
        self.client.cookies = c

        username = 'Bob'
        entity = 'ent'
        department = 'dep'
        authority = 'asset_super'
        password = '456'

        res = self.post_user_add(username, entity, department, authority, password)
        self.assertEqual(res.json()['code'], 0)

        res = self.post_user_login_normal(username, password)
        self.assertEqual(res.json()['code'], 0)

        res = self.post_user_logout_normal(username)
        self.assertEqual(res.json()['code'], 0)

        res = self.delete_user_userName(username)
        self.assertEqual(res.json()['code'], 0)

        res = self.delete_user_userName(username)
        self.assertEqual(res.json()['code'], 1)
        self.assertEqual(res.status_code, 404)

        res = self.post_user_login_normal(username, password)
        self.assertEqual(res.json()['code'], 2)

        user = User.objects.filter(username="Alice").first()
        user.system_super, user.entity_super, user.asset_super = user.set_authen("system_super")
        user.save()

        res = self.delete_user_userName("Alice")
        self.assertEqual(res.json()['code'], 2)
        self.assertEqual(res.status_code, 403)

        username = 'a' * 51
        res = self.delete_user_userName(username)
        self.assertEqual(res.json()['code'], -2)
        self.assertEqual(res.status_code, 400)

    def test_user_menu(self):
        user = User.objects.filter(username='test_user').first()
        user.token = user.generate_token()
        user.system_super, user.entity_super, user.asset_super = user.set_authen("entity_super")
        user.save()
        Token = user.token
        c = cookies.SimpleCookie()
        c['token'] = Token
        self.client.cookies = c
        # method = POST
        first = 'f_1'
        second = ''
        url = 'test'
        authority = 'entity_super/asset_super'

        res = self.post_user_menu(first, second, url, authority)
        self.assertEqual(res.json()['code'], 0)
        # test repeat first
        first = 'f_1'
        second = ''
        url = 'test'
        authority = 'entity_super/asset_super'

        res = self.post_user_menu(first, second, url, authority)
        self.assertEqual(res.json()['code'], 1)

        first = 'f_1'
        second = 's_1'
        url = 'test'
        authority = 'staff/asset_super'

        res = self.post_user_menu(first, second, url, authority)
        self.assertEqual(res.json()['code'], 0)
        #test repeat second
        first = 'f_1'
        second = 's_1'
        url = 'test'
        authority = 'entity_super/asset_super'

        res = self.post_user_menu(first, second, url, authority)
        self.assertEqual(res.json()['code'], 2)

        # test non-existed authority
        first = 'f_1'
        second = 's_2'
        url = 'test'
        authority = 'user'

        res = self.post_user_menu(first, second, url, authority)
        self.assertEqual(res.json()['code'], 3)

        #test out-range length
        url = 'u'*501
        res = self.post_user_menu(first, second, url, authority)
        self.assertEqual(res.json()['code'], -2)
        url = 'test'

        second = 's'*51
        res = self.post_user_menu(first, second, url, authority)
        self.assertEqual(res.json()['code'], -2)
        second = 's_2'

        first = 'f' * 51
        res = self.post_user_menu(first, second, url, authority)
        self.assertEqual(res.json()['code'], -2)
        first = 'f_1'

        # test authority
        user.system_super, user.entity_super, user.asset_super = user.set_authen("asset_super") 
        user.save()
        res = self.post_user_menu(first, second, url, authority)
        self.assertEqual(res.json()['code'], -2)
        self.assertEqual(res.json()['info'], '没有操作权限')

        # test token
        # token 
        Token = Token[:-1]
        c = cookies.SimpleCookie()
        c['token'] = Token
        self.client.cookies = c
        res = self.post_user_menu(first, second, url, authority)
        self.assertEqual(res.json()['code'], -2)
        self.assertEqual(res.json()['info'], 'Token不合法')

        # token does not exist
        Token = ''
        c = cookies.SimpleCookie()
        c['Token'] = Token
        self.client.cookies = c
        res = self.post_user_menu(first, second, url, authority)
        self.assertEqual(res.json()['code'], -2)
        self.assertEqual(res.json()['info'], 'Token未给出')

        # token expired
        payload = {'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=1), 'iat': datetime.datetime.utcnow(), 'username': 'Alice'}
        time.sleep(2)
        Token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        c = cookies.SimpleCookie()
        c['token'] = Token
        self.client.cookies = c
        res = self.post_user_menu(first, second, url, authority)
        self.assertEqual(res.json()['code'], -2)
        self.assertEqual(res.json()['info'], 'Token已过期')

        # method= GET
        user.token = user.generate_token()
        user.system_super, user.entity_super, user.asset_super = user.set_authen("entity_super")
        user.save()
        Token = user.token
        c = cookies.SimpleCookie()
        c['token'] = Token
        self.client.cookies = c
        res = self.get_user_menu()

        self.assertEqual(res.json()['code'], 0)

        # check entity_super
        authority = 'staff'
        user.system_super, user.entity_super, user.asset_super = user.set_authen(authority=authority)
        user.save()
        res = self.get_user_menu()

        self.assertEqual(res.json()['code'], 0)

        # check asset_super
        authority = 'asset_super'
        user.system_super, user.entity_super, user.asset_super = user.set_authen(authority=authority)
        user.save()
        res = self.get_user_menu()

        self.assertEqual(res.json()['code'], 0)
            
        # method delete
        # add 2 menu
        user.system_super, user.entity_super, user.asset_super = user.set_authen("entity_super")
        user.save()
        first = 'f_2'
        second = ''
        url = 'test'
        authority = 'entity_super/asset_super'

        res = self.post_user_menu(first, second, url, authority)
        self.assertEqual(res.json()['code'], 0)

        first = 'f_2'
        second = 's_1'
        url = 'test'
        authority = 'entity_super/asset_super'

        res = self.post_user_menu(first, second, url, authority)
        self.assertEqual(res.json()['code'], 0)

        first = 'f_3'
        second = ''
        res = self.delete_user_menu(first, second)
        self.assertEqual(res.json()['code'], 1)
        self.assertEqual(res.json()['info'], '一级菜单不存在')

        first = 'f_2'
        second = 's_2'
        res = self.delete_user_menu(first, second)
        self.assertEqual(res.json()['code'], 2)
        self.assertEqual(res.json()['info'], '二级菜单不存在')

        second = 's_1'
        res = self.delete_user_menu(first, second)
        self.assertEqual(res.json()['code'], 0)

        second = ''
        res = self.delete_user_menu(first, second)
        self.assertEqual(res.json()['code'], 0)

        # menu_list
        res = self.get_user_menu_list()
        self.assertEqual(res.json()['code'], 0)

    def test_user_department_list(self):
        user = User.objects.filter(username='test_user').first()
        user.token = user.generate_token()
        user.system_super, user.entity_super, user.asset_super = user.set_authen("entity_super")
        user.save()
        Token = user.token
        c = cookies.SimpleCookie()
        c['token'] = Token
        self.client.cookies = c

        res = self.get_user_department_list()
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], "Succeed")