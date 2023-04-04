from django.test import TestCase, Client
from User.models import User
from Department.models import Department, Entity
# Create your tests here.

class UserTests(TestCase):
    def setUp(self):
        ent = Entity.objects.create(id=1, name='en')
        dep = Department.objects.create(id=1, name='dep', entity=ent)
        User.objects.create(username='Alice', password='123', department=dep, entity=ent)

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
    
    def delete_department(self, entity_name, department_name):
        payload = {
            'entity': entity_name,
            'department': department_name,
        }
        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.delete("/department/delete", data=payload, content_type="application/json")
    
    def get_department_delete(self):
        return self.client.get(f"/department/delete")

    def test_entity_add(self):
        name = 'en1'
        res = self.post_entity_add(name)

        self.assertEqual(res.json()['code'], 0)

        name = 'en1'
        res = self.post_entity_add(name)

        self.assertEqual(res.json()['code'], 1)
        self.assertEqual(res.json()['info'], '企业实体已存在')

        res = self.get_entity_add(name)

        self.assertEqual(res.json()['code'], -3)
        self.assertEqual(res.json()['info'], 'Bad method')

        name = ''
        for i in range(60):
            name += 'a'
        res = self.post_entity_add(name)

        self.assertEqual(res.json()['code'], -2)
        self.assertEqual(res.json()['info'], 'Bad length of [entity_name]')

    def test_department_add(self):
        department = 'de1'
        entity = 'en'
        parent = ''
        res = self.post_department_add(department, entity, parent)

        self.assertEqual(res.json()['code'], 0)

        res = self.post_department_add(department, entity, parent)
        self.assertEqual(res.json()['code'], 1)
        self.assertEqual(res.json()['info'], "该部门已存在")

        department = 'de5'
        entity = 'en'
        parent = 'de1'
        res = self.post_department_add(department, entity, parent)

        self.assertEqual(res.json()['code'], 0)

        department = 'de2'
        entity = 'en1'
        res = self.post_department_add(department, entity, parent)
        self.assertEqual(res.json()['code'], 1)
        self.assertEqual(res.json()['info'], "企业实体不存在")

        department = 'de2'
        entity = 'en'
        parent = 'de3'
        res = self.post_department_add(department, entity, parent)
        self.assertEqual(res.json()['code'], 1)
        self.assertEqual(res.json()['info'], "父部门不存在")

        entity = ''
        for i in range(60):
            entity += 'a'
        res = self.post_department_add(department, entity, parent)

        self.assertEqual(res.json()['code'], -2)
        self.assertEqual(res.json()['info'], 'Bad length of [entity_name]')

        entity = 'en'
        department = ''
        for i in range(40):
            department += 'a'
        res = self.post_department_add(department, entity, parent)

        self.assertEqual(res.json()['code'], -2)
        self.assertEqual(res.json()['info'], 'Bad length of [department_name]')

        parent = ''
        department = 'de4'
        for i in range(40):
            parent += 'a'
        res = self.post_department_add(department, entity, parent)

        self.assertEqual(res.json()['code'], -2)
        self.assertEqual(res.json()['info'], 'Bad length of [parent_name]')

        en = 'en1'
        self.post_entity_add(en)
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
        self.assertEqual(res.json()['name'] , 'en')
        self.assertEqual(res.status_code, 200)

        entityName = 'en1'
        res = self.get_entity_entityName_department_list(entityName)
        self.assertEqual(res.json()['code'] , 1)
        self.assertEqual(res.status_code, 404)

        entityName = '1' * 51
        res = self.get_entity_entityName_department_list(entityName)
        self.assertEqual(res.json()['code'] , -2)
        self.assertEqual(res.status_code, 400)

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

        entity_name = 'en1'
        res = self.get_entity_name_list(entity_name)
        self.assertEqual(res.json()['code'] , -2)
        self.assertEqual(res.json()['info'], '企业实体不存在')

        entityName = '1' * 51
        res = self.get_entity_name_list(entityName)
        self.assertEqual(res.json()['code'] , -2)
        self.assertEqual(res.json()['info'], 'Bad length of [entity_name]')

        entityName = 'en'
        res = self.post_entity_name_list(entityName)
        self.assertEqual(res.json()['code'], -3)
        self.assertEqual(res.json()['info'], 'Bad method')

    def test_department_delete(self):
        entity_name = 'en0'
        department_name = 'de0'
        parent_name = ''

        # add entity
        res = self.post_entity_add(entity_name)
        self.assertEqual(res.json()['code'], 0)

        # add department
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
        entity_name = 'admin_entity'
        res = self.post_entity_add(entity_name)
        self.assertEqual(res.json()['code'], 0)

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