import random
from django.test import TestCase, Client
from User.models import User, Menu
from Department.models import Department, Entity
import hashlib
from http import cookies

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
        User.objects.create(username='Alice', password=pwd, department=dep, entity=ent)

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
    
    def get_user_menu(self):
        return self.client.get(f"/user/menu")
    
    def post_user_menu(self, first, second, url, authority):
        payload = {
            'first': first,
            'second': second,
            'authority': authority,
            'url': url
        }

        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.post("/user/menu", data=payload, content_type="application/json")
    
    def delete_user_menu(self):
        return self.client.delete("/user/menu")
    
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

        self.assertEqual(res.json()['code'], 1)

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

        # system_super is existed
        username = 'David'
        authority = 'system_super'

        res = self.post_user_add(username, entity, department, authority, password)
        self.assertEqual(res.json()['code'], 0)

        username = 'Emily'
        authority = 'system_super'

        res = self.post_user_add(username, entity, department, authority, password)
        self.assertEqual(res.json()['code'], 2)

        # asset_super
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
        # user not found
        username = 'Bob'
        password = '123'
        department = 'dep'
        authority = 'entity_super'
        res = self.post_user_edit(username, password, department, authority)
        self.assertEqual(res.json()['code'], 1)

        username = 'Bob'
        entity = 'ent'
        department = 'dep'
        authority = 'entity_super'
        password = '456'
        res = self.post_user_add(username, entity, department, authority, password)
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')

        # new password same, 3
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

        # edit authority same 3
        username = 'Bob'
        password = None
        department = None
        authority = 'entity_super'
        res = self.post_user_edit(username, password, department, authority)
        self.assertEqual(res.json()['code'], 3)

        # authority success
        username = 'Bob'
        password = None
        department = None
        authority = 'asset_super'
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
        department = 'dep'
        authority = None
        res = self.post_user_edit(username, password, department, authority)
        self.assertEqual(res.json()['code'], 3)

        # now we only have one dep, so test afterwards

        # edit both pwd and auth
        username = 'Bob'
        password = '456'
        department = None
        authority = 'entity_super'
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

    def test_user_menu(self):
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

        # method= GET
        username = 'Alice'
        password='123'
        user = User.objects.filter(username='Alice').first()
        user.token = user.generate_token()
        user.save()
        Token = user.token
        c = cookies.SimpleCookie()
        c['Token'] = Token
        self.client.cookies = c
        res = self.get_user_menu()

        self.assertEqual(res.json()['code'], 0)
        get_list = res.json()['menu']
        menu_list = Menu.objects.filter(staff_show=True)
        index=0
        for menu in get_list:
            self.assertEqual(menu['first'], menu_list[index].first)
            self.assertEqual(menu['second'], menu_list[index].second)

        # check entity_super
        authority = 'entity_super'
        user.system_super, user.entity_super, user.asset_super = user.set_authen(authority=authority)
        user.save()
        res = self.get_user_menu()

        self.assertEqual(res.json()['code'], 0)
        get_list = res.json()['menu']
        menu_list = Menu.objects.filter(entity_show=True)
        index=0
        for menu in get_list:
            self.assertEqual(menu['first'], menu_list[index].first)
            self.assertEqual(menu['second'], menu_list[index].second)

        # check asset_super
        authority = 'asset_super'
        user.system_super, user.entity_super, user.asset_super = user.set_authen(authority=authority)
        user.save()
        res = self.get_user_menu()

        self.assertEqual(res.json()['code'], 0)
        get_list = res.json()['menu']
        menu_list = Menu.objects.filter(asset_show=True)
        index=0
        print(get_list)
        print('-------')
        print(menu_list)
        for menu in get_list:
            self.assertEqual(menu['first'], menu_list[index].first)
            print(f"{menu['first']} {menu_list[index].first}")
            print(f"{menu['second']} {menu_list[index].second}")
            self.assertEqual(menu['second'], menu_list[index].second)
            index += 1
            # print(f"{menu['second']} {menu_list[index].second}")