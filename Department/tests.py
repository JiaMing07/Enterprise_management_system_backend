import random
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
        self.assertEqual(res.json()['info'], 'bad method')

    def test_department_add(self):
        department = 'de1'
        entity = 'en'
        parent = ''
        res = self.post_department_add(department, entity, parent)

        self.assertEqual(res.json()['code'], 0)

        res = self.post_department_add(department, entity, parent)
        self.assertEqual(res.json()['code'], 1)
        self.assertEqual(res.json()['info'], "该部门已存在")

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
