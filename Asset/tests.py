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
        
        dep_ent = Department.objects.create(id=1, name='ent', entity=ent)
        dep = Department.objects.create(id=2, name='dep', entity=ent)
        dep_child = Department.objects.create(id=3, name='dep_child', entity=ent, parent=dep)
        password='123'
        md5 = hashlib.md5()
        md5.update(password.encode('utf-8'))
        pwd = md5.hexdigest()
        User.objects.create(username='Alice', password=pwd, department=dep_child, entity=ent)
        User.objects.create(username='George', password=pwd, department=dep, entity=ent, asset_super=True)
        User.objects.create(username='test_attribute', password=pwd, department=dep, entity=ent)
        user = User.objects.create(username='test_user', password=pwd, department=dep, entity=ent)
        category = AssetCategory.objects.create(name='cate', entity=ent)
        Asset.objects.create(name='ass', entity=ent, owner=user.username, category=category, department=dep)
        Attribute.objects.create(id=1, name="attri_0", entity=ent, department=dep_ent)
        
    # Utility functions    
    def post_attribute_add(self, name, department):
        payload = {
            'name': name,
            'department': department
        }

        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.post("/asset/attribute/add", data=payload, content_type="application/json")
    
    def delete_attribute_delete(self, name, department):
        payload = {
            'name': name,
            'department': department
        }

        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.delete("/asset/attribute/delete", data=payload, content_type="application/json")
    
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
    
    def delete_asset_category(self, categoryName):
        payload = {
            'categoryName': categoryName,
        }

        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.delete("/asset/category/delete", data=payload, content_type="application/json")
    
    def get_asset_list(self):
        return self.client.get(f"/asset/list")
    
    def post_asset_add(self, name, parent, description, position, value, department, number, category, image):
        payload = {
            "name": name, 
            "parent": parent, 
            "description": description, 
            "position": position, 
            "value": value, 
            "department": department,
            "number": number, 
            "category": category,
            "image": image,
        }

        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.post("/asset/add", data=payload, content_type="application/json")
    
    def delete_asset(self, assetName):
        payload = {
            'assetName': assetName,
        }

        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.delete("/asset/delete", data=payload, content_type="application/json")
    
    def post_asset_attribute_add(self, asset, attribute, description):
        payload = {
            'asset': asset,
            'attribute': attribute,
            'description': description
        }

        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.post("/asset/attribute", data=payload, content_type="application/json")
    
    def get_asset_assetName(self, assetName):
        return self.client.get(f"/asset/{assetName}")
    
    def get_asset_tree(self):
        return self.client.get(f'/asset/tree')
    
    def get_category_is_number(self,category_name):
        return self.client.get(f'/asset/category/{category_name}/number')
    
    def get_asset_query(self, type, description, attribute):
        return self.client.get(f'/asset/query/{type}/{description}/{attribute}')
    
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

    def test_asset_category_delete(self):
        user = User.objects.filter(username='test_user').first()
        user.token = user.generate_token()
        user.system_super, user.entity_super, user.asset_super = user.set_authen("entity_super")
        user.save()
        Token = user.token
        c = cookies.SimpleCookie()
        c['token'] = Token
        self.client.cookies = c

        self.assertEqual(len(AssetCategory.objects.all()), 1)

        categoryName = 'category_1'
        parent = "cate"
        is_number = False
        
        res = self.post_asset_category_add(categoryName, parent, is_number)
        self.assertEqual(res.json()['info'], 'Succeed')
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(len(AssetCategory.objects.all()), 2)
        self.assertTrue(AssetCategory.objects.filter(name=categoryName).exists())

        categoryName = 'category_2'

        res = self.delete_asset_category(categoryName)
        self.assertEqual(res.json()['code'], 1)

        categoryName = 'category_1'
        
        res = self.delete_asset_category(categoryName)
        self.assertEqual(res.json()['info'], 'Succeed')
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(len(AssetCategory.objects.all()), 1)
        self.assertFalse(AssetCategory.objects.filter(name=categoryName).exists())

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
        department = 'dep'
        number = 1
        categoryName = 'cate'
        image = '127.0.0.1'
        
        res = self.post_asset_add(assetName, parentName, description, position, 
                                           value, department, number, categoryName, image)
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
        department = 'dep'
        number = 1
        categoryName = 'cate'
        image = '127.0.0.1'
        
        res = self.post_asset_add(assetName, parentName, description, position, 
                                           value, department, number, categoryName, image)
        self.assertEqual(res.json()['code'], 1)
        self.assertEqual(len(Asset.objects.all()), 3)

        # test category not found
        assetName = 'computer'
        parentName = ''
        description = 'des'
        position = 'pos'
        value = '1000'
        department = 'dep'
        number = 1
        categoryName = 'cat'
        image = '127.0.0.1'
        
        res = self.post_asset_add(assetName, parentName, description, position, 
                                           value, department, number, categoryName, image)
        self.assertEqual(res.json()['code'], 2)
        self.assertEqual(len(Asset.objects.all()), 3)

        # test department not found
        assetName = 'computer'
        parentName = ''
        description = 'des'
        position = 'pos'
        value = '1000'
        department = 'Bob'
        number = 1
        categoryName = 'cate'
        image = '127.0.0.1'
        
        res = self.post_asset_add(assetName, parentName, description, position, 
                                           value, department, number, categoryName, image)
        self.assertEqual(res.json()['code'], 3)
        self.assertEqual(len(Asset.objects.all()), 3)

        # test asset existed
        assetName = 'computer'
        parentName = ''
        description = 'des'
        position = 'pos'
        value = '1000'
        department = 'dep'
        number = 1
        categoryName = 'cate'
        image = '127.0.0.1'
        
        res = self.post_asset_add(assetName, parentName, description, position, 
                                           value, department, number, categoryName, image)
        self.assertEqual(res.json()['code'], 4)
        self.assertEqual(len(Asset.objects.all()), 3)

        # test asset/list
        res = self.get_asset_list()
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')

    def test_asset_delete(self):
        user = User.objects.filter(username='test_user').first()
        user.token = user.generate_token()
        user.system_super, user.entity_super, user.asset_super = user.set_authen("entity_super")
        user.save()
        Token = user.token
        c = cookies.SimpleCookie()
        c['token'] = Token
        self.client.cookies = c

        self.assertEqual(len(Asset.objects.all()), 1)

        assetName = 'computer'
        parentName = 'ass'
        description = 'des'
        position = 'pos'
        value = '1000'
        department = 'dep'
        number = 1
        categoryName = 'cate'
        image = '127.0.0.1'
        
        res = self.post_asset_add(assetName, parentName, description, position, 
                                           value, department, number, categoryName, image)
        self.assertEqual(res.json()['info'], 'Succeed')
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(len(Asset.objects.all()), 2)
        self.assertTrue(Asset.objects.filter(name=assetName).exists())

        assetName = 'asset_1'

        res = self.delete_asset(assetName)
        self.assertEqual(res.json()['code'], 1)

        assetName = 'computer'

        res = self.delete_asset(assetName)
        self.assertEqual(res.json()['info'], 'Succeed')
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(len(Asset.objects.all()), 1)
        self.assertFalse(Asset.objects.filter(name=assetName).exists())

        # 部门不在管理范围内
        assetName = 'computer'
        parentName = 'ass'
        description = 'des'
        position = 'pos'
        value = '1000'
        department = 'dep'
        number = 1
        categoryName = 'cate'
        image = '127.0.0.1'
        
        res = self.post_asset_add(assetName, parentName, description, position, 
                                           value, department, number, categoryName, image)
        self.assertEqual(res.json()['info'], 'Succeed')
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(len(Asset.objects.all()), 2)
        self.assertTrue(Asset.objects.filter(name=assetName).exists())

        user = User.objects.filter(username='Alice').first()
        user.token = user.generate_token()
        user.system_super, user.entity_super, user.asset_super = user.set_authen("asset_super")
        user.save()
        Token = user.token
        c = cookies.SimpleCookie()
        c['token'] = Token
        self.client.cookies = c

        assetName = 'computer'

        res = self.delete_asset(assetName)
        self.assertEqual(res.json()['code'], 2)
        self.assertTrue(Asset.objects.filter(name=assetName).exists())

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

        # not asset super or entity super, 2
        user.system_super, user.entity_super, user.asset_super = user.set_authen("staff")
        user.save()
        name = "attri_2"
        department = "dep"
        res = self.post_attribute_add(name, department)
        self.assertEqual(res.json()['code'], 2)

        # entity super, 2
        user.system_super, user.entity_super, user.asset_super = user.set_authen("entity_super")
        user.save()
        name = "attri_2"
        department = "dep"
        res = self.post_attribute_add(name, department)
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')

        user.system_super, user.entity_super, user.asset_super = user.set_authen("asset_super")
        user.save()

        # not department or son department, 2
        name = "attri_3"
        department = "ent"
        res = self.post_attribute_add(name, department)
        self.assertEqual(res.json()['code'], 2)
        self.assertEqual(res.json()['info'], "没有添加该部门自定义属性的权限")

        # son department, 0
        name = "attri_4"
        department = "dep_child"
        res = self.post_attribute_add(name, department)
        self.assertEqual(res.json()['info'], 'Succeed')
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
        # department = "dep_child"
        # res = self.get_attribute_list(department)
        # self.assertEqual(res.json()['info'], '没有查看该部门自定义属性的权限')
        # self.assertEqual(res.json()['code'], 1)

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

        # entity_super
        user.system_super, user.entity_super, user.asset_super = user.set_authen("entity_super")
        user.save()

        # entity_super, dep, 0
        department = "dep"
        res = self.get_attribute_list(department)
        self.assertEqual(res.json()['info'], 'Succeed')
        self.assertEqual(res.json()['code'], 0)

        # entity_super, dep_child, 0
        department = "dep_child"
        res = self.get_attribute_list(department)
        self.assertEqual(res.json()['info'], 'Succeed')
        self.assertEqual(res.json()['code'], 0)

        # entity_super, ent, 0
        department = "ent"
        res = self.get_attribute_list(department)
        self.assertEqual(res.json()['info'], 'Succeed')
        self.assertEqual(res.json()['code'], 0)

    def test_asset_attribute_add(self):

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
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')

        # asset length 50, Bad length of []
        asset = "123456789012345678901234567890123456789012345678901234567890"
        attribute = "attri_1"
        description = "This is a description."
        res = self.post_asset_attribute_add(asset, attribute, description)
        # self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Bad length of [asset]')

        # attribute length 50, Bad length of []
        asset = "1"
        attribute = "123456789012345678901234567890123456789012345678901234567890"
        description = "This is a description."
        res = self.post_asset_attribute_add(asset, attribute, description)
        # self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Bad length of [attribute]')

        # description length 300, Bad length of []
        # asset = "1"
        # attribute = "2"
        # description = "This is a description."
        # res = self.post_asset_attribute_add(asset, attribute, description)
        # # self.assertEqual(res.json()['code'], 0)
        # self.assertEqual(res.json()['info'], 'Bad length of [description]')

        # not asset_super, 2, "只有资产管理员可为资产添加属性"
        user.system_super, user.entity_super, user.asset_super = user.set_authen("staff")
        user.save()

        asset = "1"
        attribute = "2"
        description = "This is a description."
        res = self.post_asset_attribute_add(asset, attribute, description)
        self.assertEqual(res.json()['code'], 2)
        self.assertEqual(res.json()['info'], "只有资产管理员可为资产添加属性")

        # asset not exist, 1, "资产不存在"
        user.system_super, user.entity_super, user.asset_super = user.set_authen("asset_super")
        user.save()

        asset = "bss"
        attribute = "attri_1"
        description = "This is a description."
        res = self.post_asset_attribute_add(asset, attribute, description)
        self.assertEqual(res.json()['code'], 1)
        self.assertEqual(res.json()['info'], "资产不存在")

        # attribute not exist, 1, "自定义属性不存在"
        asset = "ass"
        attribute = "attri_111"
        description = "This is a description."
        res = self.post_asset_attribute_add(asset, attribute, description)
        self.assertEqual(res.json()['code'], 1)
        self.assertEqual(res.json()['info'], "自定义属性不存在")

        # success, 0
        asset = "ass"
        attribute = "attri_1"
        description = "This is a description."
        res = self.post_asset_attribute_add(asset, attribute, description)
        # self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], "Succeed")

    def test_attribute_delete(self):
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
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')

        # not exist, 1, "该部门不存在该自定义属性"
        name = "attri_4"
        department = "dep"
        res = self.delete_attribute_delete(name, department)
        self.assertEqual(res.json()['code'], 1)
        self.assertEqual(res.json()['info'], "该部门不存在该自定义属性")

        # staff, 2, "没有删除该部门自定义属性的权限"
        user.system_super, user.entity_super, user.asset_super = user.set_authen("staff")
        user.save()

        name = "attri_3"
        department = "dep_child"
        res = self.delete_attribute_delete(name, department)
        self.assertEqual(res.json()['code'], 2)
        self.assertEqual(res.json()['info'], "没有删除该部门自定义属性的权限")

        # not son department or self department
        user.system_super, user.entity_super, user.asset_super = user.set_authen("asset_super")
        user.save()

        name = "attri_0"
        department = "ent"
        res = self.delete_attribute_delete(name, department)
        # self.assertEqual(res.json()['code'], 2)
        self.assertEqual(res.json()['info'], "没有删除该部门自定义属性的权限")

        # succeed
        name = "attri_3"
        department = "dep_child"
        res = self.delete_attribute_delete(name, department)
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], "Succeed")

        # succeed
        name = "attri_2"
        department = "dep"
        res = self.delete_attribute_delete(name, department)
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], "Succeed")

    def test_get_asset_assetName(self):
        user = User.objects.filter(username='test_user').first()
        user.token = user.generate_token()
        user.system_super, user.entity_super, user.asset_super = user.set_authen("asset_super")
        user.save()
        Token = user.token
        c = cookies.SimpleCookie()
        c['token'] = Token
        self.client.cookies = c

        self.assertEqual(len(Asset.objects.all()), 1)

        assetName = 'computer'
        parentName = 'ass'
        description = 'des'
        position = 'pos'
        value = '1000'
        department = 'dep'
        number = 1
        categoryName = 'cate'
        image = '127.0.0.1'
        
        res = self.post_asset_add(assetName, parentName, description, position, 
                                           value, department, number, categoryName, image)
        self.assertEqual(res.json()['info'], 'Succeed')
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(len(Asset.objects.all()), 2)
        self.assertTrue(Asset.objects.filter(name=assetName).exists())

        attributeName = "GPU"
        department = "dep"
        res = self.post_attribute_add(attributeName, department)
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')

        assetName = "computer"
        attributeName = "GPU"
        description = "RTX4090"
        res = self.post_asset_attribute_add(assetName, attributeName, description)
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], "Succeed")

        assetName = 'computer'
        res = self.get_asset_assetName(assetName)
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], "Succeed")
        self.assertEqual(res.json()['property']['GPU'], "RTX4090")
        self.assertEqual(res.json()['property']['assetName'], f"{assetName}")

        assetName = 'asset_1'
        res = self.get_asset_assetName(assetName)
        self.assertEqual(res.json()['code'], 1)

    def test_asset_tree(self):
        user = User.objects.filter(username='test_user').first()
        user.token = user.generate_token()
        user.system_super, user.entity_super, user.asset_super = user.set_authen("entity_super")
        user.save()
        Token = user.token
        c = cookies.SimpleCookie()
        c['token'] = Token
        self.client.cookies = c

        res = self.get_asset_tree()
        self.assertEqual(res.json()['info'], "Succeed")

    def test_category_is_number(self):
        user = User.objects.filter(username='test_user').first()
        user.token = user.generate_token()
        user.system_super, user.entity_super, user.asset_super = user.set_authen("entity_super")
        user.save()
        Token = user.token
        c = cookies.SimpleCookie()
        c['token'] = Token
        self.client.cookies = c
        category_name = 'cate'

        res = self.get_category_is_number(category_name)
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], "Succeed")

        category_name = 'c_1'
        res = self.get_category_is_number(category_name)
        self.assertEqual(res.json()['code'], 1)
        self.assertEqual(res.json()['info'], "不存在此资产")

    def test_asset_query(self):
        user = User.objects.filter(username='test_user').first()
        user.token = user.generate_token()
        user.system_super, user.entity_super, user.asset_super = user.set_authen("entity_super")
        user.save()
        Token = user.token
        c = cookies.SimpleCookie()
        c['token'] = Token
        self.client.cookies = c
        
        # type = "asset_name"
        type = "asset_name"
        description = "a"
        attribute = "1"

        res = self.get_asset_query(type, description, attribute)
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')

        # type = "asset_description"
        type = "asset_description"
        description = "a"
        attribute = "1"

        res = self.get_asset_query(type, description, attribute)
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')
        
        # type = "asset_position"
        type = "asset_position"
        description = "a"
        attribute = "1"

        res = self.get_asset_query(type, description, attribute)
        self.assertEqual(res.json()['info'], 'Succeed')
        self.assertEqual(res.json()['code'], 0)

        # type = "asset_type"
        type = "asset_type"
        description = "a"
        attribute = "1"

        res = self.get_asset_query(type, description, attribute)
        self.assertEqual(res.json()['info'], 'Succeed')
        self.assertEqual(res.json()['code'], 0)

        # type = "asset_status"
        type = "asset_status"
        description = "a"
        attribute = "1"

        res = self.get_asset_query(type, description, attribute)
        self.assertEqual(res.json()['info'], 'Succeed')
        self.assertEqual(res.json()['code'], 0)
        
        # type = "asset_department"
        type = "asset_department"
        description = "a"
        attribute = "1"

        res = self.get_asset_query(type, description, attribute)
        self.assertEqual(res.json()['info'], 'Succeed')
        self.assertEqual(res.json()['code'], 0)

        # error_type
        type = "department"
        description = "a"
        attribute = "1"

        res = self.get_asset_query(type, description, attribute)
        self.assertEqual(res.json()['code'], 1)
        self.assertEqual(res.json()['info'], '此搜索类型不存在')