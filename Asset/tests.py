from django.test import TestCase

from User.models import User, Menu
from Department.models import Department, Entity
from Asset.models import Attribute, Asset, AssetAttribute, AssetCategory

from http import cookies
import hashlib

# Create your tests here.

# Test for Attribute
class AttributeTests(TestCase):
    def test_for_unit(self):
        self.assertNotEqual(0, 1)
    
    # Initializer
    def setUp(self):
        ent = Entity.objects.create(id=1, name='ent')
        attri_0 = Attribute.objects.create(id=1, name="attri_0", entity=ent)
        dep_ent = Department.objects.create(id=1, name='ent', entity=ent)
        dep = Department.objects.create(id=2, name='dep', entity=ent)
        dep_child = Department.objects.create(id=3, name='dep_child', entity=ent, parent=dep)
        password='123'
        md5 = hashlib.md5()
        md5.update(password.encode('utf-8'))
        pwd = md5.hexdigest()
        User.objects.create(username='Alice', password=pwd, department=dep, entity=ent)
        User.objects.create(username='test_attribute', password=pwd, department=dep, entity=ent)

    def post_attribute_add(self, name, department):
        payload = {
            'name': name,
            'department': department
        }

        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.post("/asset/attribute/add", data=payload, content_type="application/json")

    def test_attribute_add(self):

        # token
        user = User.objects.filter(username='test_attribute').first()
        user.token = user.generate_token()
        user.system_super, user.entity_super, user.asset_super = user.set_authen("asset_super")
        user.save()
        Token = user.token
        c = cookies.SimpleCookie()
        c['token'] = Token
        self.client.cookies = c

        # success
        name = "attri_1"
        department = "dep"
        res = self.post_attribute_add(name, department)
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')

        # not asset super, 2
        user.system_super, user.entity_super, user.asset_super = user.set_authen("entity_super")
        user.save()
        name = "attri_2"
        department = "dep"
        res = self.post_attribute_add(name, department)
        self.assertEqual(res.json()['code'], 2)

        user.system_super, user.entity_super, user.asset_super = user.set_authen("asset_super")
        user.save()

        # not department or son department, 2
        name = "attri_2"
        department = "dep_ent"
        res = self.post_attribute_add(name, department)
        self.assertEqual(res.json()['code'], 2)

        # son department, 0
        name = "attri_2"
        department = "dep_child"
        res = self.post_attribute_add(name, department)
        self.assertEqual(res.json()['code'], 2)

        # same, 1
        name = "attri_0"
        res = self.post_attribute_add(name)
        self.assertEqual(res.json()['code'], 1)

        # same, 1
        name = "attri_1"
        res = self.post_attribute_add(name)
        self.assertEqual(res.json()['code'], 1)