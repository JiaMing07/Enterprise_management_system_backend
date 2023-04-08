from django.test import TestCase

from User.models import User, Menu
from Department.models import Department, Entity
from Asset.models import Attribute, Asset, AssetAttribute, AssetCategory

# Create your tests here.

# Test for Attribute
class AttributeTests(TestCase):
    def test_for_unit(self):
        self.assertNotEqual(0, 1)
    
    # Initializer
    def setUp(self):
        ent = Entity.objects.create(id=1, name='ent')
        attri_0 = Attribute.objects.create(id=1, name="attri_0", entity=ent)

    def post_attribute_add(self, name):
        payload = {
            'name': name
        }

        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.post("/asset/attribute/add", data=payload, content_type="application/json")

    def test_attribute_add(self):

        # success
        name = "attri_1"
        res = self.post_attribute_add(name)
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')

        # same, 1
        name = "attri_0"
        res = self.post_attribute_add(name)
        self.assertEqual(res.json()['code'], 1)

        # same, 1
        name = "attri_1"
        res = self.post_attribute_add(name)
        self.assertEqual(res.json()['code'], 1)