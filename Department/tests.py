from django.test import TestCase, Client
from User.models import User
from Department.models import Department, Entity
import hashlib
from http import cookies
# Create your tests here.

class DepartmentTests(TestCase):
    def setUp(self):
        ent = Entity.objects.create(id=1, name='en')
        dep_ent = Department.objects.create(id=1, name='en', entity=ent)
        dep = Department.objects.create(id=2,name='dep', entity=ent)
        password='123'
        md5 = hashlib.md5()
        md5.update(password.encode('utf-8'))
        pwd = md5.hexdigest()
        User.objects.create(username='Alice', password=pwd, department=dep, entity=ent)
        User.objects.create(username='test_user', password=pwd, department=dep, entity=ent)

    def post_department_add(self, department_name, entity_name, parent_name):
        payload = {
            'entity': entity_name,
            'department': department_name,
            'parent': parent_name
        }

        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.post("/department/add", data=payload, content_type="application/json")
    
    def post_entity_add(self, entity_name):
        payload = {
            'name': entity_name,
        }

        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.post("/entity/add", data=payload, content_type="application/json")
    
    def get_department_add(self, department_name, entity_name, parent_name):
        payload = {
            'entity': entity_name,
            'department': department_name,
            'parent': parent_name
        }

        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.get("/department/add", data=payload, content_type="application/json")

    def get_entity_add(self, entity_name):
        payload = {
            'name': entity_name,
        }

        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.get("/entity/add", data=payload, content_type="application/json")
    
    def get_entity_entityName_department_list(self, entity_name):
        return self.client.get(f"/entity/{entity_name}/department/list")
    
    def post_entity_entityName_department_list(self, entity_name):
        return self.client.post(f"/entity/{entity_name}/department/list")
    
    def get_entity_list(self):
        return self.client.get("/entity/list")
    
    def get_entity_name_list(self, entity_name):
        return self.client.get(f"/entity/{entity_name}/list")
    
    def post_entity_name_list(self, entity_name):
        return self.client.post(f"/entity/{entity_name}/list")
    
    def get_entity_entityName_entitySuper(self, entityName):
        return self.client.get(f"/entity/{entityName}/entitySuper")
    
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
    
    # Now start testcases. 
    
    def delete_department(self, entity_name, department_name):
        payload = {
            'entity': entity_name,
            'department': department_name,
        }
        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.delete("/department/delete", data=payload, content_type="application/json")
    
    def get_department_delete(self):
        return self.client.get(f"/department/delete")

    def delete_entity_delete(self, entity_name):
        return self.client.delete(f"/entity/{entity_name}/delete")
    
    def get_entity_delete(self, entity_name):
        return self.client.get(f"/entity/{entity_name}/delete")
    
    def test_entity_add(self):
        user = User.objects.filter(username='test_user').first()
        user.token = user.generate_token()
        user.system_super, user.entity_super, user.asset_super = user.set_authen("system_super")
        user.save()
        Token = user.token
        c = cookies.SimpleCookie()
        c['token'] = Token
        self.client.cookies = c
        # successfully add
        name = 'en1'
        res = self.post_entity_add(name)

        self.assertEqual(res.json()['code'], 0)

        # add an already exist entity
        name = 'en1'
        res = self.post_entity_add(name)

        self.assertEqual(res.json()['code'], 1)
        self.assertEqual(res.json()['info'], '企业实体已存在')

        # bad method
        res = self.get_entity_add(name)

        self.assertEqual(res.json()['code'], -3)
        self.assertEqual(res.json()['info'], 'Bad method')

        # entity_name out of range
        name = ''
        for i in range(60):
            name += 'a'
        res = self.post_entity_add(name)

        self.assertEqual(res.json()['code'], -2)
        self.assertEqual(res.json()['info'], 'Bad length of [entity_name]')

        # bad authority
        user.system_super, user.entity_super, user.asset_super = user.set_authen("entity_super")
        user.save()
        name = 'en2'
        res = self.post_entity_add(name)

        self.assertEqual(res.json()['code'], -2)
        self.assertEqual(res.json()['info'], '没有操作权限')

    def test_department_add(self):
        user = User.objects.filter(username='test_user').first()
        user.token = user.generate_token()
        user.system_super, user.entity_super, user.asset_super = user.set_authen("entity_super")
        user.save()
        Token = user.token
        c = cookies.SimpleCookie()
        c['token'] = Token
        self.client.cookies = c
        # successfully add department
        department = 'de1'
        entity = 'en'
        parent = ''
        res = self.post_department_add(department, entity, parent)

        self.assertEqual(res.json()['code'], 0)

        # add an already existed department
        res = self.post_department_add(department, entity, parent)
        self.assertEqual(res.json()['code'], 1)
        self.assertEqual(res.json()['info'], "该部门已存在")

        # set parent for department
        department = 'de5'
        entity = 'en'
        parent = 'de1'
        res = self.post_department_add(department, entity, parent)

        self.assertEqual(res.json()['code'], 0)

        # entity not exist
        department = 'de2'
        entity = 'en1'
        res = self.post_department_add(department, entity, parent)
        self.assertEqual(res.json()['code'], 1)
        self.assertEqual(res.json()['info'], "企业实体不存在")

        # parent department does not exist
        department = 'de2'
        entity = 'en'
        parent = 'de3'
        res = self.post_department_add(department, entity, parent)
        self.assertEqual(res.json()['code'], 1)
        self.assertEqual(res.json()['info'], "父部门不存在")

        # entity_name out of range
        entity = ''
        for i in range(60):
            entity += 'a'
        res = self.post_department_add(department, entity, parent)

        self.assertEqual(res.json()['code'], -2)
        self.assertEqual(res.json()['info'], 'Bad length of [entity_name]')

        # department_name out of range
        entity = 'en'
        department = ''
        for i in range(40):
            department += 'a'
        res = self.post_department_add(department, entity, parent)

        self.assertEqual(res.json()['code'], -2)
        self.assertEqual(res.json()['info'], 'Bad length of [department_name]')

        # parent_name out of range
        parent = ''
        department = 'de4'
        for i in range(40):
            parent += 'a'
        res = self.post_department_add(department, entity, parent)

        self.assertEqual(res.json()['code'], -2)
        self.assertEqual(res.json()['info'], 'Bad length of [parent_name]')

        user.system_super, user.entity_super, user.asset_super = user.set_authen("system_super")
        user.save()
        en = 'en1'
        self.post_entity_add(en)
        user.system_super, user.entity_super, user.asset_super = user.set_authen("entity_super")
        user.save()
        department = 'de_1'
        parent = 'de1'
        res = self.post_department_add(department, en, parent)
        self.assertEqual(res.json()['code'], 1)
        self.assertEqual(res.json()['info'], '父部门不存在')

    def test_get_entity_list(self):
        res = self.get_entity_list()
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.status_code, 200)

    def test_get_entity_entityName_department_list(self):
        entityName = 'en'
        res = self.get_entity_entityName_department_list(entityName)
        self.assertEqual(res.json()['code'] , 0)
        self.assertEqual(res.json()['entityName'] , 'en')
        self.assertEqual(res.status_code, 200)

        # entity does not exist
        entityName = 'en1'
        res = self.get_entity_entityName_department_list(entityName)
        self.assertEqual(res.json()['code'] , 1)
        self.assertEqual(res.status_code, 404)

        # entityName out of range
        entityName = '1' * 51
        res = self.get_entity_entityName_department_list(entityName)
        self.assertEqual(res.json()['code'] , -2)
        self.assertEqual(res.status_code, 400)

        # bad method
        entityName = 'en'
        res = self.post_entity_entityName_department_list(entityName)
        self.assertEqual(res.json()['code'], -3)
        self.assertEqual(res.json()['info'], 'Bad method')

    def test_entity_name_list(self):
        entity_name = 'en'
        res = self.get_entity_name_list(entity_name)
        self.assertEqual(res.json()['code'] , 0)
        self.assertEqual(res.json()['name'] , 'en')
        self.assertEqual(res.status_code, 200)

        # entity does not exist
        entity_name = 'en1'
        res = self.get_entity_name_list(entity_name)
        self.assertEqual(res.json()['code'] , -2)
        self.assertEqual(res.json()['info'], '企业实体不存在')

        # entity_name out of range
        entityName = '1' * 51
        res = self.get_entity_name_list(entityName)
        self.assertEqual(res.json()['code'] , -2)
        self.assertEqual(res.json()['info'], 'Bad length of [entity_name]')

        # bad method
        entityName = 'en'
        res = self.post_entity_name_list(entityName)
        self.assertEqual(res.json()['code'], -3)
        self.assertEqual(res.json()['info'], 'Bad method')

    def test_get_entity_entityName_entitySuper(self):
        user = User.objects.filter(username='test_user').first()
        user.token = user.generate_token()
        user.system_super, user.entity_super, user.asset_super = user.set_authen("system_super")
        user.save()
        Token = user.token
        c = cookies.SimpleCookie()
        c['token'] = Token
        self.client.cookies = c
    
        entity = 'en'
        res = self.get_entity_entityName_entitySuper(entity)
        self.assertEqual(res.json()['code'], 2)
        self.assertEqual(res.status_code, 404)

        username = 'Bob'
        entity = 'en'
        department = 'dep'
        authority = 'entity_super'
        password = '456'
        res = self.post_user_add(username, entity, department, authority, password)
        self.assertEqual(res.json()['code'], 0)

        res = self.get_entity_entityName_entitySuper(entity)
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')
        self.assertEqual(res.json()['username'], 'Bob')

        entity = 'en1'
        res = self.get_entity_entityName_entitySuper(entity)
        self.assertEqual(res.json()['code'], 1)
        self.assertEqual(res.status_code, 404)

        entity = 'a' * 51
        res = self.get_entity_entityName_entitySuper(entity)
        self.assertEqual(res.json()['code'], -2)
        self.assertEqual(res.status_code, 400)


    def test_department_delete(self):
        user = User.objects.filter(username='test_user').first()
        user.token = user.generate_token()
        user.system_super, user.entity_super, user.asset_super = user.set_authen("system_super")
        user.save()
        Token = user.token
        c = cookies.SimpleCookie()
        c['token'] = Token
        self.client.cookies = c

        entity_name = 'en0'
        department_name = 'de0'
        parent_name = ''

        # add entity
        res = self.post_entity_add(entity_name)
        self.assertEqual(res.json()['code'], 0)

        # add department
        user.system_super, user.entity_super, user.asset_super = user.set_authen("entity_super")
        user.save()
        res = self.post_department_add(department_name, entity_name, parent_name)
        self.assertEqual(res.json()['code'], 0)

        # department_name length wrong
        entity_name = 'en0'
        department_name = '1234567890123456789012345678901234' # > 30
        res = self.delete_department(entity_name, department_name)
        self.assertEqual(res.json()['info'], "Bad length of [department_name]")

        # entity_name length wrong, code 400
        entity_name = '123456789012345678901234567890123456789012345678901234567890' # > 50
        department_name = 'de0'
        res = self.delete_department(entity_name, department_name)
        self.assertEqual(res.json()['info'], "Bad length of [entity_name]")

        # entity not exist, 1
        entity_name = 'en1'
        department_name = 'de0'
        res = self.delete_department(entity_name, department_name)
        self.assertEqual(res.json()['info'], "企业实体不存在")
        self.assertEqual(res.status_code, 403)
        self.assertEqual(res.json()['code'], 1)

        # department not exist, 1
        entity_name = 'en0'
        department_name = 'de1'
        res = self.delete_department(entity_name, department_name)
        self.assertEqual(res.json()['code'], 1)

        # admin_entity, 2
        user.system_super, user.entity_super, user.asset_super = user.set_authen("system_super")
        user.save()
        entity_name = 'admin_entity'
        res = self.post_entity_add(entity_name)
        self.assertEqual(res.json()['code'], 0)

        user.system_super, user.entity_super, user.asset_super = user.set_authen("entity_super")
        user.save()
        department_name = 'de1'
        res = self.delete_department(entity_name, department_name)
        self.assertEqual(res.json()['code'], 2)
        self.assertEqual(res.json()['info'], "不可删除超级管理员所在的企业实体")

        # delete success
        entity_name = 'en0'
        department_name = 'de0'
        res = self.delete_department(entity_name, department_name)
        self.assertEqual(res.json()['code'], 0)

        # bad method
        res = self.get_department_delete()
        self.assertEqual(res.json()['code'], -3)
        self.assertEqual(res.json()['info'], "Bad method")

    def test_entity_entity_name_delete(self):
        user = User.objects.filter(username='test_user').first()
        user.token = user.generate_token()
        user.system_super, user.entity_super, user.asset_super = user.set_authen("system_super")
        user.save()
        Token = user.token
        c = cookies.SimpleCookie()
        c['token'] = Token
        self.client.cookies = c
        entity_name = 'en1'
        res = self.post_entity_add(entity_name)

        self.assertEqual(res.json()['code'], 0)
        
        # successfully delete entity
        res = self.delete_entity_delete(entity_name)
        self.assertEqual(res.json()['code'], 0)

        # entity does not exist
        res = self.delete_entity_delete(entity_name)
        self.assertEqual(res.json()['code'], 1)
        self.assertEqual(res.json()['info'], "企业实体不存在")

        entity_name = 'admin_entity'
        res = self.post_entity_add(entity_name)

        self.assertEqual(res.json()['code'], 0)

        # can't delete admin_entity
        entity_name = 'admin_entity'
        res = self.delete_entity_delete(entity_name)
        self.assertEqual(res.json()['code'], 2)
        self.assertEqual(res.json()['info'], "不可删除超级管理员所在的企业实体")

        # bad method
        res = self.get_entity_delete(entity_name)
        self.assertEqual(res.json()['code'], -3)
        self.assertEqual(res.json()['info'], "Bad method")