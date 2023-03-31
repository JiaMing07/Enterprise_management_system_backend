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
    
    def delete_entity_delete(self, entity_name):
        return self.client.delete(f"/entity/{entity_name}/delete")
    
    def get_entity_delete(self, entity_name):
        return self.client.get(f"/entity/{entity_name}/delete")
    
    def test_entity_add(self):
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

    def test_department_add(self):
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

    def test_entity_entity_name_delete(self):
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