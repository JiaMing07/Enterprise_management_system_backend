from django.test import TestCase, Client
from Asset.models import AssetCategory, Asset, Attribute, AssetAttribute
from Department.models import Department, Entity
from User.models import User
import hashlib
from http import cookies

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
        # attri_0 = Attribute.objects.create(id=1, name="attri_0", entity=ent)
        dep_ent = Department.objects.create(id=1, name='ent', entity=ent)
        dep = Department.objects.create(id=2, name='dep', entity=ent)
        dep_child = Department.objects.create(id=3, name='dep_child', entity=ent, parent=dep)
        password='123'
        md5 = hashlib.md5()
        md5.update(password.encode('utf-8'))
        pwd = md5.hexdigest()
        User.objects.create(username='Alice', password=pwd, department=dep, entity=ent)
        User.objects.create(username='test_attribute', password=pwd, department=dep, entity=ent)
        user = User.objects.create(username='test_user', password=pwd, department=dep, entity=ent)
        category = AssetCategory.objects.create(name='cate', entity=ent)
        Asset.objects.create(name='ass', entity=ent, owner=user.username, category=category)
        
    # Utility functions    
    def post_attribute_add(self, name, department):
        payload = {
            'name': name,
            'department': department
        }

        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.post("/asset/attribute/add", data=payload, content_type="application/json")
    
    def get_attribute_list(self, department):
        return self.client.get(f"/asset/attribute/{department}/list")
    
    def get_asset_category_list(self):
        return self.client.get(f"/asset/category/list")
    
    def post_asset_category_add(self, name, parent, is_number):
        payload = {
            'name': name,
            'parent': parent,
            'is_number': is_number,
        }

        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.post("/asset/category/add", data=payload, content_type="application/json")
    
    def get_asset_list(self):
        return self.client.get(f"/asset/list")
    
    def post_asset_add(self, name, parent, description, position, value, owner, number, category, image):
        payload = {
            "name": name, 
            "parent": parent, 
            "description": description, 
            "position": position, 
            "value": value, 
            "owner": owner,
            "number": number, 
            "category": category,
            "image": image,
        }

        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.post("/asset/add", data=payload, content_type="application/json")
    
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

        self.assertEqual(len(AssetCategory.objects.all()), 1)

        # test parent=''
        categoryName = 'category_1'
        parent = ""
        is_number = False
        
        res = self.post_asset_category_add(categoryName, parent, is_number)
        self.assertEqual(res.json()['info'], 'Succeed')
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(len(AssetCategory.objects.all()), 3)
        self.assertTrue(AssetCategory.objects.filter(name=categoryName).exists())

        # test parent not found
        categoryName = 'category_2'
        parent = "cat"
        is_number = False
        
        res = self.post_asset_category_add(categoryName, parent, is_number)
        self.assertEqual(res.json()['code'], 1)
        self.assertEqual(len(AssetCategory.objects.all()), 3)

        # test category existed
        categoryName = 'category_1'
        parent = "cate"
        is_number = False
        
        res = self.post_asset_category_add(categoryName, parent, is_number)
        self.assertEqual(res.json()['code'], 2)
        self.assertEqual(len(AssetCategory.objects.all()), 3)

        # test asset/category/list
        res = self.get_asset_category_list()
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')

    def test_asset_add(self):
        user = User.objects.filter(username='test_user').first()
        user.token = user.generate_token()
        user.system_super, user.entity_super, user.asset_super = user.set_authen("entity_super")
        user.save()
        Token = user.token
        c = cookies.SimpleCookie()
        c['token'] = Token
        self.client.cookies = c

        self.assertEqual(len(Asset.objects.all()), 1)

        # test parent=''
        assetName = 'computer'
        parentName = ''
        description = 'des'
        position = 'pos'
        value = '1000'
        owner = 'Alice'
        number = 1
        categoryName = 'cate'
        image = '127.0.0.1'
        
        res = self.post_asset_add(assetName, parentName, description, position, 
                                           value, owner, number, categoryName, image)
        self.assertEqual(res.json()['info'], 'Succeed')
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(len(Asset.objects.all()), 3)
        self.assertTrue(Asset.objects.filter(name=assetName).exists())

        # test parent not found
        assetName = 'computer'
        parentName = 'as'
        description = 'des'
        position = 'pos'
        value = '1000'
        owner = 'Alice'
        number = 1
        categoryName = 'cate'
        image = '127.0.0.1'
        
        res = self.post_asset_add(assetName, parentName, description, position, 
                                           value, owner, number, categoryName, image)
        self.assertEqual(res.json()['code'], 1)
        self.assertEqual(len(Asset.objects.all()), 3)

        # test category not found
        assetName = 'computer'
        parentName = ''
        description = 'des'
        position = 'pos'
        value = '1000'
        owner = 'Alice'
        number = 1
        categoryName = 'cat'
        image = '127.0.0.1'
        
        res = self.post_asset_add(assetName, parentName, description, position, 
                                           value, owner, number, categoryName, image)
        self.assertEqual(res.json()['code'], 2)
        self.assertEqual(len(Asset.objects.all()), 3)

        # test owner not found
        assetName = 'computer'
        parentName = ''
        description = 'des'
        position = 'pos'
        value = '1000'
        owner = 'Bob'
        number = 1
        categoryName = 'cate'
        image = '127.0.0.1'
        
        res = self.post_asset_add(assetName, parentName, description, position, 
                                           value, owner, number, categoryName, image)
        self.assertEqual(res.json()['code'], 3)
        self.assertEqual(len(Asset.objects.all()), 3)

        # test asset existed
        assetName = 'computer'
        parentName = ''
        description = 'des'
        position = 'pos'
        value = '1000'
        owner = 'Alice'
        number = 1
        categoryName = 'cate'
        image = '127.0.0.1'
        
        res = self.post_asset_add(assetName, parentName, description, position, 
                                           value, owner, number, categoryName, image)
        self.assertEqual(res.json()['code'], 4)
        self.assertEqual(len(Asset.objects.all()), 3)

        # test asset/list
        res = self.get_asset_list()
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')

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
        name = "attri_3"
        department = "ent"
        res = self.post_attribute_add(name, department)
        # self.assertEqual(res.json()['code'], 2)
        self.assertEqual(res.json()['info'], "没有添加该部门自定义属性的权限")

        # son department, 0
        name = "attri_2"
        department = "dep_child"
        res = self.post_attribute_add(name, department)
        self.assertEqual(res.json()['code'], 0)

        # same, 1
        name = "attri_1"
        department = "dep"
        res = self.post_attribute_add(name, department)
        self.assertEqual(res.json()['code'], 1)

        # same, 1
        name = "attri_2"
        department = "dep_child"
        res = self.post_attribute_add(name, department)
        self.assertEqual(res.json()['code'], 1)

    def test_attribute_list(self):
        # token
        user = User.objects.filter(username='test_attribute').first()
        user.token = user.generate_token()
        user.system_super, user.entity_super, user.asset_super = user.set_authen("asset_super")
        user.save()
        Token = user.token
        c = cookies.SimpleCookie()
        c['token'] = Token
        self.client.cookies = c

        # add 1, dep
        name = "attri_1"
        department = "dep"
        res = self.post_attribute_add(name, department)
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')

        # add 2, dep
        name = "attri_2"
        department = "dep"
        res = self.post_attribute_add(name, department)
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')

        # add 3, dep_child
        name = "attri_3"
        department = "dep_child"
        res = self.post_attribute_add(name, department)
        # self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')

        # add 4, dep_child
        name = "attri_4"
        department = "dep_child"
        res = self.post_attribute_add(name, department)
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')

        # staff, not same dep, 1
        user.system_super, user.entity_super, user.asset_super = user.set_authen("staff")
        user.save()

        # staff, son dep, 1
        department = "dep_child"
        res = self.get_attribute_list(department)
        self.assertEqual(res.json()['info'], '没有查看该部门自定义属性的权限')
        self.assertEqual(res.json()['code'], 1)

        # staff, same dep, 0
        department = "dep"
        res = self.get_attribute_list(department)
        self.assertEqual(res.json()['info'], 'Succeed')
        self.assertEqual(res.json()['code'], 0)

        # asset_super
        user.system_super, user.entity_super, user.asset_super = user.set_authen("asset_super")
        user.save()

        # own department, 0
        department = "dep"
        res = self.get_attribute_list(department)
        self.assertEqual(res.json()['info'], 'Succeed')
        self.assertEqual(res.json()['code'], 0)

        # asset_super, son department, 0
        department = "dep_child"
        res = self.get_attribute_list(department)
        self.assertEqual(res.json()['info'], 'Succeed')
        self.assertEqual(res.json()['code'], 0)
