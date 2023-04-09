from django.test import TestCase, Client
from Asset.models import AssetCategory, Asset, Attribute, AssetAttribute
from Department.models import Department, Entity
from User.models import User
import hashlib
from http import cookies

# Create your tests here.
class AssetTests(TestCase):
    def setUp(self):
        ent = Entity.objects.create(id=1, name='ent')
        dep_ent = Department.objects.create(id=1, name='ent', entity=ent)
        dep = Department.objects.create(id=2,name='dep', entity=ent)
        password='123'
        md5 = hashlib.md5()
        md5.update(password.encode('utf-8'))
        pwd = md5.hexdigest()
        User.objects.create(username='Alice', password=pwd, department=dep, entity=ent)
        User.objects.create(username='test_user', password=pwd, department=dep, entity=ent)
        AssetCategory.objects.create(name='cate', entity=ent)

    # Utility functions
    def get_asset_category_list(self):
        return self.client.get(f"/asset/category/list")
    
    def post_asset_category_add(self, name, parent):
        payload = {
            'name': name,
            'parent': parent
        }

        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.post("/asset/category/add", data=payload, content_type="application/json")
    
    # Now start testcases. 
    def test_asset_category_add(self):
        user = User.objects.filter(username='test_user').first()
        user.token = user.generate_token()
        user.system_super, user.entity_super, user.asset_super = user.set_authen("entity_super")
        user.save()
        Token = user.token
        c = cookies.SimpleCookie()
        c['token'] = Token
        self.client.cookies = c

        self.assertGreaterEqual(len(AssetCategory.objects.all()), 1)

        categoryName = 'category_1'
        parent = 'cate'
        
        res = self.post_asset_category_add(categoryName, parent)
        self.assertEqual(res.json()['info'], 'Succeed')
        self.assertEqual(res.json()['code'], 0)
        self.assertGreaterEqual(len(AssetCategory.objects.all()), 2)
        self.assertTrue(AssetCategory.objects.filter(name=categoryName).exists())

        res = self.get_asset_category_list()
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')