from django.test import TestCase, Client
from Asset.models import AssetCategory, Asset, Attribute, AssetAttribute
from Department.models import Department, Entity
from User.models import User
import hashlib
from http import cookies

from User.models import User, Menu
from Department.models import Department, Entity
from Asset.models import Attribute, Asset, AssetAttribute, AssetCategory, Label

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
    def create_token(self, name, authority):
        user = User.objects.filter(username=name).first()
        user.token = user.generate_token()
        user.system_super, user.entity_super, user.asset_super = user.set_authen(authority)
        user.save()
        Token = user.token
        c = cookies.SimpleCookie()
        c['token'] = Token
        self.client.cookies = c
        return user
      
    def post_attribute_add(self, name, department):
        payload = {
            'name': name,
            'department': department
        }

        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.post("/asset/attribute/add", data=payload, content_type="application/json")
    
    def post_asset_category_add(self, name, parent, is_number):
        payload = {
            'name': name,
            'parent': parent,
            'is_number': is_number,
        }

        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.post("/asset/category/add", data=payload, content_type="application/json")
    
    def post_asset_add(self, name, parent, description, position, value, department, number, category, life, image):
        payload = {
            "name": name, 
            "parent": parent, 
            "description": description, 
            "position": position, 
            "value": value, 
            "department": department,
            "number": number, 
            "category": category,
            "life": life,
            "image": image,
        }

        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.post("/asset/add", data=payload, content_type="application/json")
    
    def post_asset_add_list(self, assets):
        payload = {
            "assets": assets,
        }

        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.post("/asset/add/list", data=payload, content_type="application/json")
    
    def post_asset_attribute_add(self, asset, attribute, description):
        payload = {
            'asset': asset,
            'attribute': attribute,
            'description': description
        }

        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.post("/asset/attribute", data=payload, content_type="application/json")
    
    def post_asset_label(self, name, labels):
        payload = {
            'name': name,
            'labels': labels
        }

        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.post("/asset/label", data=payload, content_type="application/json")
    
    # Utility functions    
    def put_attribute_edit(self, name, newName, department, newDepartment):
        payload = {
            'name': name,
            'new_name': newName,
            'department': department,
            'new_depart':newDepartment
        }

        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.put("/asset/attribute/edit", data=payload, content_type="application/json")
    
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
    
    def put_asset_category_edit(self, oldName, name, parent, is_number):
        payload = {
            'oldName': oldName,
            'name': name,
            'parent': parent,
            'is_number': is_number,
        }

        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.put("/asset/category/edit", data=payload, content_type="application/json")
    
    def delete_asset_category(self, categoryName):
        payload = {
            'categoryName': categoryName,
        }

        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.delete("/asset/category/delete", data=payload, content_type="application/json")
    
    def get_asset_list(self):
        return self.client.get(f"/asset/list")
    
    def get_asset_idle(self):
        return self.client.get(f"/asset/idle")
    
    def put_asset_edit(self, oldName, name, parent, description, position, value, owner, number, state, category, life, image):
        payload = {
            'oldName': oldName,
            "name": name, 
            "parent": parent, 
            "description": description, 
            "position": position, 
            "value": value, 
            "owner": owner,
            "number": number,
            "state": state,
            "category": category,
            "life": life,
            "image": image,
        }

        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.put("/asset/edit", data=payload, content_type="application/json")
    
    def delete_asset_retire(self, assetName):
        payload = {
            'assetName': assetName,
        }

        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.delete("/asset/retire", data=payload, content_type="application/json")
    
    def delete_asset(self, assetName):
        payload = {
            'assetName': assetName,
        }

        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.delete("/asset/delete", data=payload, content_type="application/json")

    def get_asset_attribute_list(self, assetName):
        return self.client.get(f"/asset/attribute/{assetName}")
    
    def delete_asset_attribute(self, asset, attribute):
        payload = {
            'asset': asset,
            'attribute': attribute
        }

        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.delete("/asset/attribute", data=payload, content_type="application/json")
    
    def get_asset_assetSuper(self):
        return self.client.get("/asset/assetSuper")
    
    def get_asset_user_query(self):
        return self.client.get(f'/asset/user')
    
    def get_asset_assetName(self, assetName):
        return self.client.get(f"/asset/{assetName}")
    
    def get_asset_tree(self):
        return self.client.get(f'/asset/tree')
    
    def get_category_is_number(self,category_name):
        return self.client.get(f'/asset/category/{category_name}/number')
    
    def get_asset_query(self, type, description, attribute):
        return self.client.get(f'/asset/query/{type}/{description}/{attribute}')
    
    def get_asset_user_query(self):
        return self.client.get(f'/asset/user') 
    
    def get_asset_user_query(self):
        return self.client.get(f'/asset/user')
    
    def get_asset_assetName(self, assetName):
        return self.client.get(f"/asset/{assetName}")
    
    def get_asset_tree(self):
        return self.client.get(f'/asset/tree')
    
    def get_category_is_number(self,category_name):
        return self.client.get(f'/asset/category/{category_name}/number')
    
    def get_asset_query(self, type, description, attribute):
        return self.client.get(f'/asset/query/{type}/{description}/{attribute}')
    
    def get_asset_user_query(self):
        return self.client.get(f'/asset/user')
    
    def put_asset_allocate(self, assets, department, asset_super):
        payload = {
            "name": assets,
            "department": department,
            "asset_super": asset_super
        }
        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.put("/asset/allocate", data=payload, content_type="application/json")
    
    def get_asset_label(self):
        return self.client.get(f'/asset/label')
    
    def post_asset_warning(self, asset, ageLimit, numberLimit):
        payload = {
            "asset": asset,
            "ageLimit": ageLimit,
            "numberLimit": numberLimit,
        }

        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.post("/asset/warning", data=payload, content_type="application/json")
    
    def get_asset_warning(self):
        return self.client.get("/asset/warning")
    
    def put_asset_warning_assetName(self, assetName, ageLimit, numberLimit):
        payload = {
            "ageLimit": ageLimit,
            "numberLimit": numberLimit,
        }

        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.put(f"/asset/{assetName}/warning", data=payload, content_type="application/json")
    
    def get_asset_warning_assetName(self, assetName):
        return self.client.get(f"/asset/{assetName}/warning")
    
    def delete_asset_warning_assetName(self, assetName):
        return self.client.delete(f"/asset/{assetName}/warning")

    def get_asset_warning_message(self):
        return self.client.get("/asset/warning/message")
    
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

    def test_asset_category_edit(self):
        user = User.objects.filter(username='test_user').first()
        user.token = user.generate_token()
        user.system_super, user.entity_super, user.asset_super = user.set_authen("entity_super")
        user.save()
        Token = user.token
        c = cookies.SimpleCookie()
        c['token'] = Token
        self.client.cookies = c

        categoryName = 'category_1'
        parent = "cate"
        is_number = False
        
        res = self.post_asset_category_add(categoryName, parent, is_number)
        self.assertEqual(res.json()['info'], 'Succeed')
        self.assertEqual(res.json()['code'], 0)

        self.assertEqual(len(AssetCategory.objects.all()), 2)
        oldName = 'category_1'
        self.assertTrue(AssetCategory.objects.filter(name=oldName).exists())
        newName = 'category_2'
        parent = "cate"
        is_number = True

        res = self.put_asset_category_edit(oldName, newName, parent, is_number)
        self.assertEqual(res.json()['info'], 'Succeed')
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(len(AssetCategory.objects.all()), 2)
        self.assertFalse(AssetCategory.objects.filter(name=oldName).exists())
        self.assertTrue(AssetCategory.objects.filter(name=newName).exists())

        res = self.put_asset_category_edit(oldName, newName, parent, is_number)
        self.assertEqual(res.json()['code'], 1)

        oldName = 'cate'
        res = self.put_asset_category_edit(oldName, newName, parent, is_number)
        self.assertEqual(res.json()['code'], 2)

        oldName = 'category_2'
        newName = 'category_1'
        parent = "category_3"
        res = self.put_asset_category_edit(oldName, newName, parent, is_number)
        self.assertEqual(res.json()['code'], 3)

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
        life = 5
        image = '127.0.0.1'
        
        res = self.post_asset_add(assetName, parentName, description, position, 
                                           value, department, number, categoryName, life, image)
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
        life = 5
        image = '127.0.0.1'
        
        res = self.post_asset_add(assetName, parentName, description, position, 
                                           value, department, number, categoryName, life, image)
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
        life = 5
        image = '127.0.0.1'
        
        res = self.post_asset_add(assetName, parentName, description, position, 
                                           value, department, number, categoryName, life, image)
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
        life = 5
        image = '127.0.0.1'
        
        res = self.post_asset_add(assetName, parentName, description, position, 
                                           value, department, number, categoryName, life, image)
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
        life = 5
        image = '127.0.0.1'
        
        res = self.post_asset_add(assetName, parentName, description, position, 
                                           value, department, number, categoryName, life, image)
        self.assertEqual(res.json()['code'], 4)
        self.assertEqual(len(Asset.objects.all()), 3)

        # test asset/list
        res = self.get_asset_list()
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')

    def test_asset_edit(self):
        user = User.objects.filter(username='test_user').first()
        user.token = user.generate_token()
        user.system_super, user.entity_super, user.asset_super = user.set_authen("entity_super")
        user.save()
        Token = user.token
        c = cookies.SimpleCookie()
        c['token'] = Token
        self.client.cookies = c

        assetName = 'computer'
        parentName = 'ass'
        description = 'des'
        position = 'pos'
        value = '1000'
        department = 'dep'
        number = 1
        categoryName = 'cate'
        life = 5
        image = '127.0.0.1'
        
        res = self.post_asset_add(assetName, parentName, description, position, 
                                           value, department, number, categoryName, life, image)
        self.assertEqual(res.json()['info'], 'Succeed')
        self.assertEqual(res.json()['code'], 0)

        oldName = 'computer'
        self.assertEqual(len(Asset.objects.all()), 2)
        self.assertTrue(Asset.objects.filter(name=oldName).exists())
        newName = 'mobile phone'
        parentName = 'ass'
        description = 'des'
        position = 'pos'
        value = '1000'
        owner = 'Alice'
        number = 1
        state = 'IN_USE'
        categoryName = 'cate'
        life = 5
        image = '127.0.0.1'

        res = self.put_asset_edit(oldName, newName, parentName, description, position, 
                                  value, owner, number, state, categoryName, life, image)
        self.assertEqual(res.json()['info'], 'Succeed')
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(len(Asset.objects.all()), 2)
        self.assertFalse(Asset.objects.filter(name=oldName).exists())
        self.assertTrue(Asset.objects.filter(name=newName).exists())
        
        res = self.put_asset_edit(oldName, newName, parentName, description, position, 
                                  value, owner, number, state, categoryName, life, image)
        self.assertEqual(res.json()['code'], 1)

        oldName = 'mobile phone'
        newName = 'ass'
        res = self.put_asset_edit(oldName, newName, parentName, description, position, 
                                  value, owner, number, state, categoryName, life, image)
        self.assertEqual(res.json()['code'], 2)

        newName = 'computer'
        categoryName = 'category_1'
        res = self.put_asset_edit(oldName, newName, parentName, description, position, 
                                  value, owner, number, state, categoryName, life, image)
        self.assertEqual(res.json()['code'], 3)

        owner = 'Bob'
        categoryName = 'cate'
        res = self.put_asset_edit(oldName, newName, parentName, description, position, 
                                  value, owner, number, state, categoryName, life, image)
        self.assertEqual(res.json()['code'], 4)

        owner = 'Alice'
        parentName = 'asset_1'
        res = self.put_asset_edit(oldName, newName, parentName, description, position, 
                                  value, owner, number, state, categoryName, life, image)
        self.assertEqual(res.json()['code'], 7)

        parentName = 'ass'

        user = User.objects.filter(username='Alice').first()
        user.token = user.generate_token()
        user.system_super, user.entity_super, user.asset_super = user.set_authen("asset_super")
        user.save()
        Token = user.token
        c = cookies.SimpleCookie()
        c['token'] = Token
        self.client.cookies = c

        owner = 'test_user'
        res = self.put_asset_edit(oldName, newName, parentName, description, position, 
                                  value, owner, number, state, categoryName, life, image)
        self.assertEqual(res.json()['code'], 6)

        owner = 'Alice'
        oldName = 'ass'
        res = self.put_asset_edit(oldName, newName, parentName, description, position, 
                                  value, owner, number, state, categoryName, life, image)
        self.assertEqual(res.json()['code'], 5)

    def test_asset_retire(self):
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
        life = 5
        image = '127.0.0.1'
        
        res = self.post_asset_add(assetName, parentName, description, position, 
                                           value, department, number, categoryName, life, image)
        self.assertEqual(res.json()['info'], 'Succeed')
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(len(Asset.objects.all()), 2)
        self.assertTrue(Asset.objects.filter(name=assetName).exists())

        assetName = ['asset_1']

        res = self.delete_asset_retire(assetName)
        self.assertEqual(res.json()['code'], 1)
        self.assertEqual(res.json()['info'], 'asset asset_1 not found')

        assetName = ['computer']

        res = self.delete_asset_retire(assetName)
        self.assertEqual(res.json()['info'], 'Succeed')
        self.assertEqual(res.json()['code'], 0)
        # self.assertEqual(len(Asset.objects.all()), 2)
        # self.assertTrue(Asset.objects.filter(name=assetName).exists())

        # 部门不在管理范围内
        assetName = ['computer1']
        parentName = 'ass'
        description = 'des'
        position = 'pos'
        value = '1000'
        department = 'dep'
        number = 1
        categoryName = 'cate'
        life = 5
        image = '127.0.0.1'
        
        res = self.post_asset_add(assetName, parentName, description, position, 
                                           value, department, number, categoryName, life, image)
        self.assertEqual(res.json()['info'], 'Succeed')
        self.assertEqual(res.json()['code'], 0)
        # self.assertEqual(len(Asset.objects.all()), 2)
        # self.assertTrue(Asset.objects.filter(name=assetName).exists())

        user = User.objects.filter(username='Alice').first()
        user.token = user.generate_token()
        user.system_super, user.entity_super, user.asset_super = user.set_authen("asset_super")
        user.save()
        Token = user.token
        c = cookies.SimpleCookie()
        c['token'] = Token
        self.client.cookies = c

        assetName = ['computer']

        res = self.delete_asset_retire(assetName)
        self.assertEqual(res.json()['code'], 1)
        self.assertEqual(res.json()['info'], "资产 computer 的部门不在管理范围内")
        # self.assertTrue(Asset.objects.filter(name=assetName).exists())

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

        # not asset_super, 2, 
        user.system_super, user.entity_super, user.asset_super = user.set_authen("staff")
        user.save()

        asset = "1"
        attribute = "2"
        description = "This is a description."
        res = self.post_asset_attribute_add(asset, attribute, description)
        self.assertEqual(res.json()['code'], -2)
        # self.assertEqual(res.json()['info'], "只有资产管理员可为资产添加属性")

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

    def test_attribute_edit(self):
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

        # add 4, dep_child
        name = "attri_4"
        department = "dep_child"
        res = self.post_attribute_add(name, department)
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')

        # new_name length, "Bad length of [attribute_name]"
        name = "attri_1"
        new_name = "123456789012345678901234567890123456789012345678901234567890"
        department = "dep"
        new_depart_name = None
        res = self.put_attribute_edit(name, new_name, department, new_depart_name)
        self.assertEqual(res.json()['info'], "Bad length of [attribute_name]")
        # self.assertEqual(res.json()['code'], 1)

        # attribute not exist, "该部门不存在该自定义属性", 1
        name = "attri_4"
        new_name = "attri_5"
        department = "dep"
        new_depart_name = None
        res = self.put_attribute_edit(name, new_name, department, new_depart_name)
        self.assertEqual(res.json()['info'], "该部门不存在该自定义属性")
        self.assertEqual(res.json()['code'], 1)

        # department not exist, "该企业不存在该部门", 1
        name = "attri_4"
        new_name = "attri_5"
        department = "depdep"
        new_depart_name = None
        res = self.put_attribute_edit(name, new_name, department, new_depart_name)
        self.assertEqual(res.json()['info'], "该企业不存在该部门")
        self.assertEqual(res.json()['code'], 1)

        # department has new_attri, "当前部门已存在该属性", 3
        name = "attri_1"
        new_name = "attri_2"
        department = "dep"
        new_depart_name = None
        res = self.put_attribute_edit(name, new_name, department, new_depart_name)
        self.assertEqual(res.json()['info'], "当前部门已存在该属性")
        self.assertEqual(res.json()['code'], 3)

        # asset_super, "没有修改该部门自定义属性名称的权限", 2
        name = "attri_0"
        new_name = "attri_2"
        department = "ent"
        new_depart_name = None
        res = self.put_attribute_edit(name, new_name, department, new_depart_name)
        self.assertEqual(res.json()['info'], "没有修改该部门自定义属性名称的权限")
        self.assertEqual(res.json()['code'], 2)

        # asset_super, son_depart, "Succeed", 0
        name = "attri_3"
        new_name = "attri_33"
        department = "dep_child"
        new_depart_name = None
        res = self.put_attribute_edit(name, new_name, department, new_depart_name)
        self.assertEqual(res.json()['info'], "Succeed")
        self.assertEqual(res.json()['code'], 0)

        # asset_super, own_depart, "Succeed", 0
        name = "attri_1"
        new_name = "attri_11"
        department = "dep"
        new_depart_name = None
        res = self.put_attribute_edit(name, new_name, department, new_depart_name)
        self.assertEqual(res.json()['info'], "Succeed")
        self.assertEqual(res.json()['code'], 0)

        # staff, "没有修改该部门自定义属性名称的权限", 2
        user.system_super, user.entity_super, user.asset_super = user.set_authen("staff")
        user.save()

        name = "attri_11"
        new_name = "attri_111"
        department = "dep"
        new_depart_name = None
        res = self.put_attribute_edit(name, new_name, department, new_depart_name)
        self.assertEqual(res.json()['info'], "没有修改该部门自定义属性名称的权限")
        self.assertEqual(res.json()['code'], 2)

        # new_depart, "新部门已存在该属性", 3
        user.system_super, user.entity_super, user.asset_super = user.set_authen("asset_super")
        user.save()

        name = "attri_2"
        new_name = "attri_33"
        department = "dep"
        new_depart_name = "dep_child"
        res = self.put_attribute_edit(name, new_name, department, new_depart_name)
        self.assertEqual(res.json()['info'], "新部门已存在该属性")
        self.assertEqual(res.json()['code'], 3)

        # entity_super, all depart in entity, "Succeed", 0
        user.system_super, user.entity_super, user.asset_super = user.set_authen("entity_super")
        user.save()

        name = "attri_0"
        new_name = "attri_00"
        department = "ent"
        new_depart_name = None
        res = self.put_attribute_edit(name, new_name, department, new_depart_name)
        self.assertEqual(res.json()['info'], "Succeed")
        self.assertEqual(res.json()['code'], 0)

        # entity_super, all depart in entity, "Succeed", 0
        name = "attri_00"
        new_name = "attri_000"
        department = "ent"
        new_depart_name = "dep_child"
        res = self.put_attribute_edit(name, new_name, department, new_depart_name)
        self.assertEqual(res.json()['info'], "Succeed")
        self.assertEqual(res.json()['code'], 0)

    def test_get_asset_attribute_list(self):

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

        # success, 0
        asset = "ass"
        attribute = "attri_1"
        description = "This is a description."
        res = self.post_asset_attribute_add(asset, attribute, description)
        # self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], "Succeed")

        # success, 0
        asset = "ass"
        attribute = "attri_2"
        description = "This is a description 2."
        res = self.post_asset_attribute_add(asset, attribute, description)
        # self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], "Succeed")

        # success, 0
        asset = "ass"
        attribute = "attri_3"
        description = "This is a description 3."
        res = self.post_asset_attribute_add(asset, attribute, description)
        # self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], "Succeed")

        # 1, "企业不存在该资产"
        asset = "bss"
        res = self.get_asset_attribute_list(asset)
        # self.assertEqual(res.json()['code'], 1)
        self.assertEqual(res.json()['info'], "企业不存在该资产")

        # 0, succeed
        asset = "ass"
        res = self.get_asset_attribute_list(asset)
        # self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], "Succeed")

    def test_asset_attribute_delete(self):

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

        # add 4, dep_child
        name = "attri_4"
        department = "dep_child"
        res = self.post_attribute_add(name, department)
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')

        # success, 0
        asset = "ass"
        attribute = "attri_1"
        description = "This is a description."
        res = self.post_asset_attribute_add(asset, attribute, description)
        # self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], "Succeed")

        # success, 0
        asset = "ass"
        attribute = "attri_2"
        description = "This is a description 2."
        res = self.post_asset_attribute_add(asset, attribute, description)
        # self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], "Succeed")

        # success, 0
        asset = "ass"
        attribute = "attri_3"
        description = "This is a description 3."
        res = self.post_asset_attribute_add(asset, attribute, description)
        # self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], "Succeed")

        # 2, "没有删除资产属性的权限"
        user.system_super, user.entity_super, user.asset_super = user.set_authen("staff")
        user.save()

        asset = "ass"
        attribute = "attri_3"
        res = self.delete_asset_attribute(asset, attribute)
        self.assertEqual(res.json()['info'], "没有删除资产属性的权限")
        self.assertEqual(res.json()['code'], 2)

        # 1, "资产不存在"
        user.system_super, user.entity_super, user.asset_super = user.set_authen("entity_super")
        user.save()

        asset = "bss"
        attribute = "attri_3"
        res = self.delete_asset_attribute(asset, attribute)
        self.assertEqual(res.json()['info'], "资产不存在")
        self.assertEqual(res.json()['code'], 1)

        # 1, "自定义属性不存在"
        asset = "ass"
        attribute = "attri_6"
        res = self.delete_asset_attribute(asset, attribute)
        self.assertEqual(res.json()['info'], "自定义属性不存在")
        self.assertEqual(res.json()['code'], 1)

        # 1, "资产没有该属性"
        asset = "ass"
        attribute = "attri_0"
        res = self.delete_asset_attribute(asset, attribute)
        self.assertEqual(res.json()['info'], "资产没有该属性")
        self.assertEqual(res.json()['code'], 1)

        # 0, "success"
        asset = "ass"
        attribute = "attri_3"
        res = self.delete_asset_attribute(asset, attribute)
        self.assertEqual(res.json()['info'], "Succeed")
        self.assertEqual(res.json()['code'], 0)

    def test_asset_assetSuper(self):
        user = User.objects.filter(username='test_user').first()
        user.token = user.generate_token()
        user.system_super, user.entity_super, user.asset_super = user.set_authen("asset_super")
        user.save()
        Token = user.token
        c = cookies.SimpleCookie()
        c['token'] = Token
        self.client.cookies = c

        res = self.get_asset_assetSuper()
        self.assertEqual(res.json()['info'], "Succeed")
        self.assertEqual(res.json()['code'], 0)

    def test_asset_user_query(self):
        user = User.objects.filter(username='test_user').first()
        user.token = user.generate_token()
        user.system_super, user.entity_super, user.asset_super = user.set_authen("entity_super")
        user.save()
        Token = user.token
        c = cookies.SimpleCookie()
        c['token'] = Token
        self.client.cookies = c

        res = self.get_asset_user_query()
        self.assertEqual(res.json()['info'], "Succeed")
        self.assertEqual(res.json()['code'], 0)

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
        life = 5
        image = '127.0.0.1'
        
        res = self.post_asset_add(assetName, parentName, description, position, 
                                           value, department, number, categoryName, life, image)
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
        self.assertEqual(res.json()['info'], "Succeed")
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

        # type = "asset_department"
        type = "asset_owner"
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

    def test_asset_add_list(self):
        user = User.objects.filter(username='Alice').first()
        user.token = user.generate_token()
        user.system_super, user.entity_super, user.asset_super = user.set_authen("asset_super")
        user.save()
        Token = user.token
        c = cookies.SimpleCookie()
        c['token'] = Token
        self.client.cookies = c

        self.assertEqual(len(Asset.objects.all()), 1)

        assets = [
            {
            "name": 'computer', 
            "parent": '', 
            "description": 'work', 
            "position": 'desk', 
            "value": 5999, 
            "department": 'dep_child',
            "number": 1, 
            "category": 'cate',
            "life": 5,
            "image": '127.0.0.1',
            },
            {
            "name": 'keyboard', 
            "parent": 'computer', 
            "description": 'work', 
            "position": 'desk', 
            "value": 100, 
            "department": '',
            "number": 1, 
            "category": 'cate',
            "life": 5,
            "image": '127.0.0.2',
            "state": 'IN_USE',
            "owner": 'Alice',
            },
            {
            "name": 'keyboard', 
            "parent": 'asset_1', #parent not found
            "description": 'work', 
            "position": 'desk', 
            "value": 100, 
            "department": '',
            "number": 1, 
            "category": 'cate',
            "life": 5,
            "image": '127.0.0.2',
            },
            {
            "name": 'keyboard', 
            "parent": 'computer', 
            "description": 'work', 
            "position": 'desk', 
            "value": 100, 
            "department": 'department_1',# department not found
            "number": 1, 
            "category": 'cate',
            "life": 5,
            "image": '127.0.0.2',
            },
            {
            "name": 'keyboard', 
            "parent": 'computer', 
            "description": 'work', 
            "position": 'desk', 
            "value": 100, 
            "department": 'dep_child',
            "number": 1, 
            "category": 'category_1',# category not found
            "life": 5,
            "image": '127.0.0.2',
            },
            {
            "name": 'keyboard',# repeat
            "parent": 'computer', 
            "description": 'work', 
            "position": 'desk', 
            "value": 100, 
            "department": 'dep_child',
            "number": 1, 
            "category": 'cate',
            "life": 5,
            "image": '127.0.0.2',
            },
            {
            "name": 'mouse', 
            "parent": 'computer', 
            "description": 'work', 
            "position": 'desk', 
            "value": 100, 
            "department": 'dep_child',
            "number": 1, 
            "category": 'cate',
            "life": 5,
            "image": '127.0.0.3',
            "owner": 'Bob',# owner not found
            },
            {
            "name": 'mouse', 
            "parent": 'computer', 
            "description": 'work', 
            "position": 'desk', 
            "value": 100, 
            "department": 'dep',# 部门不在管理范围内
            "number": 1, 
            "category": 'cate',
            "life": 5,
            "image": '127.0.0.3',
            }
        ]

        res = self.post_asset_add_list(assets)
        self.assertEqual(res.json()['code'], 1)
        self.assertEqual(len(Asset.objects.all()), 4)
        self.assertTrue(Asset.objects.filter(name='ass').exists())
        self.assertTrue(Asset.objects.filter(name='computer').exists())
        self.assertTrue(Asset.objects.filter(name='ent').exists())
        self.assertTrue(Asset.objects.filter(name='keyboard').exists())
    
    def test_asset_delete(self):
        self.create_token('test_user', 'entity_super')

        self.assertEqual(len(Asset.objects.all()), 1)

        assetName = 'computer'
        parentName = 'ass'
        description = 'des'
        position = 'pos'
        value = '1000'
        department = 'dep'
        number = 1
        categoryName = 'cate'
        life = 5
        image = '127.0.0.1'
        
        res = self.post_asset_add(assetName, parentName, description, position, 
                                           value, department, number, categoryName, life, image)
        self.assertEqual(res.json()['info'], 'Succeed')
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(len(Asset.objects.all()), 2)
        self.assertTrue(Asset.objects.filter(name=assetName).exists())

        assetName = 'asset_1'

        res = self.delete_asset(assetName)
        self.assertEqual(res.json()['code'], 1)

        assetName = ['computer']

        res = self.delete_asset_retire(assetName)
        self.assertEqual(res.json()['code'], 0)

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
        life = 5
        image = '127.0.0.1'
        
        res = self.post_asset_add(assetName, parentName, description, position, 
                                           value, department, number, categoryName, life, image)
        self.assertEqual(res.json()['info'], 'Succeed')
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(len(Asset.objects.all()), 2)
        self.assertTrue(Asset.objects.filter(name=assetName).exists())

        self.create_token('Alice', 'entity_super')
        assetName = 'computer'

        res = self.delete_asset(assetName)
        self.assertEqual(res.json()['code'], 2)
        self.assertTrue(Asset.objects.filter(name=assetName).exists())

        self.create_token('test_user', 'entity_super')
        res = self.delete_asset(assetName)
        self.assertEqual(res.json()['code'], 3)
        self.assertEqual(res.json()['info'], '不能删除未清退的资产')

        res = self.delete_asset_retire([assetName])
        self.assertEqual(res.json()['code'], 0)

        res = self.delete_asset(assetName)
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')
    
    def test_asset_idle(self):
        user = self.create_token('test_user', 'asset_super')
        
        res = self.get_asset_idle()
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')

    def test_asset_allocate(self):
        ent = Entity.objects.filter(name='ent').first()
        category = AssetCategory.objects.filter(name='cate').first()
        dep = Department.objects.filter(name='dep').first()
        dep_child = Department.objects.filter(name='dep_child').first()
        Asset.objects.create(name='asset_1', entity=ent, owner='test_user', category=category, department=dep)
        Asset.objects.create(name='asset_2', entity=ent, owner='Alice', category=category, department=dep_child)
        user = self.create_token('Alice', 'asset_super')

        assets = ["as"]
        department = "dep"
        asset_super = "test_user"

        res = self.put_asset_allocate(assets, department, asset_super)
        self.assertEqual(res.json()['info'], "第1条资产 as 不存在")
        self.assertEqual(res.json()['code'], 1)

        # ass 不在管辖范围内，asset_2 不在闲置中
        asset = Asset.objects.filter(name='asset_2').first()
        asset.state = 'IN_USE'
        asset.save()
        assets = ["ass", "asset_2"]
        department = "dep"
        asset_super = "test_user"

        res = self.put_asset_allocate(assets, department, asset_super)
        self.assertEqual(res.json()['info'], "第1条资产 ass 不在管辖范围内，无法调拨；第2条资产 asset_2 不在闲置中，无法调拨")
        self.assertEqual(res.json()['code'], 1)

        user = self.create_token('test_user', 'asset_super')
        asset = Asset.objects.filter(name='asset_1').first()
        asset.state = 'IDLE'
        asset.save()
        assets = ["asset_1"]
        department = "dep_child"
        asset_super = "Alice"

        res = self.put_asset_allocate(assets, department, asset_super)
        self.assertEqual(res.json()['info'], "Succeed")
        self.assertEqual(res.json()['code'], 0)

    def test_asset_label_post(self):
        user = User.objects.filter(username='Alice').first()
        user.token = user.generate_token()
        user.system_super, user.entity_super, user.asset_super = user.set_authen("staff")
        user.save()
        Token = user.token
        c = cookies.SimpleCookie()
        c['token'] = Token
        self.client.cookies = c

        # authentication
        name = "model_1"
        labels = ["资产名称"]
        res = self.post_asset_label(name, labels)
        # self.assertEqual(res.json()['code'], 1)
        self.assertEqual(res.json()['info'], '没有操作权限')

        user.system_super, user.entity_super, user.asset_super = user.set_authen("asset_super")
        user.save()

        name = "model_1"
        labels = ["资产名称"]
        res = self.post_asset_label(name, labels)
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')

        # same name, 2
        name = "model_1"
        labels = ["资产名称", "归属公司"]
        res = self.post_asset_label(name, labels)
        self.assertEqual(res.json()['code'], 2)
        self.assertEqual(res.json()['info'], '重名')

        name = "model_2"
        labels = ["资产名称", "归属公司"]
        res = self.post_asset_label(name, labels)
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')

        name = "model_3"
        labels = ["资产名称", "归属公司","资产类型", "资产挂账部门", "资产自定义属性", 
                  "资产数量", "资产位置", "资产描述", "资产二维码", "资产价值"]
        res = self.post_asset_label(name, labels)
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')

    def test_asset_label_get(self):
        user = User.objects.filter(username='Alice').first()
        user.token = user.generate_token()
        user.system_super, user.entity_super, user.asset_super = user.set_authen("asset_super")
        user.save()
        Token = user.token
        c = cookies.SimpleCookie()
        c['token'] = Token
        self.client.cookies = c

        name = "model_1"
        labels = ["资产名称"]
        res = self.post_asset_label(name, labels)
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')

        name = "model_2"
        labels = ["资产名称", "归属公司"]
        res = self.post_asset_label(name, labels)
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')

        name = "model_3"
        labels = ["资产名称", "归属公司","资产类型", "资产挂账部门", "资产自定义属性", 
                  "资产数量", "资产位置", "资产描述", "资产二维码", "资产价值"]
        res = self.post_asset_label(name, labels)
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')

        res = self.get_asset_label()
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')

    def test_asset_warning(self):
        user = User.objects.filter(username='test_user').first()
        user.token = user.generate_token()
        user.system_super, user.entity_super, user.asset_super = user.set_authen("asset_super")
        user.save()
        Token = user.token
        c = cookies.SimpleCookie()
        c['token'] = Token
        self.client.cookies = c

        assetName = 'computer'
        parentName = 'ass'
        description = 'des'
        position = 'pos'
        value = '1000'
        department = 'dep'
        number = 3
        categoryName = 'cate'
        life = 3
        image = '127.0.0.1'
        
        res = self.post_asset_add(assetName, parentName, description, position, 
                                           value, department, number, categoryName, life, image)
        self.assertEqual(res.json()['info'], 'Succeed')
        self.assertEqual(res.json()['code'], 0)

        assetName = 'asset_1'
        ageLimit = 2
        numberLimit = 2

        res = self.post_asset_warning(assetName, ageLimit, numberLimit)
        self.assertEqual(res.json()['code'], 1)

        assetName = 'computer'

        res = self.post_asset_warning(assetName, ageLimit, numberLimit)
        self.assertEqual(res.json()['info'], 'Succeed')
        self.assertEqual(res.json()['code'], 0)

        res = self.post_asset_warning(assetName, ageLimit, numberLimit)
        self.assertEqual(res.json()['code'], 2)

        assetName = 'keyboard'
        parentName = 'computer'
        description = 'des'
        position = 'pos'
        value = '1000'
        department = 'dep_child'
        number = 3
        categoryName = 'cate'
        life = 3
        image = '127.0.0.1'
        
        res = self.post_asset_add(assetName, parentName, description, position, 
                                           value, department, number, categoryName, life, image)
        self.assertEqual(res.json()['info'], 'Succeed')
        self.assertEqual(res.json()['code'], 0)

        res = self.put_asset_edit(assetName, assetName, parentName, description, position, 
                                           value, 'Alice', number, 'IDLE', categoryName, life, image)
        self.assertEqual(res.json()['info'], 'Succeed')
        self.assertEqual(res.json()['code'], 0)

        ageLimit = 2
        numberLimit = 2

        res = self.post_asset_warning(assetName, ageLimit, numberLimit)
        self.assertEqual(res.json()['info'], 'Succeed')
        self.assertEqual(res.json()['code'], 0)

        res = self.get_asset_warning()
        self.assertEqual(res.json()['info'], 'Succeed')
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(len(res.json()['warnings']), 2)

        res = self.get_asset_warning_message()
        self.assertEqual(res.json()['info'], 'Succeed')
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(len(res.json()['messages']), 0)

        assetName = 'asset_1'
        ageLimit = 2
        numberLimit = 4

        res = self.put_asset_warning_assetName(assetName, ageLimit, numberLimit)
        self.assertEqual(res.json()['code'], 1)

        assetName = 'keyboard'

        res = self.put_asset_warning_assetName(assetName, ageLimit, numberLimit)
        self.assertEqual(res.json()['info'], 'Succeed')
        self.assertEqual(res.json()['code'], 0)

        res = self.get_asset_warning_message()
        self.assertEqual(res.json()['info'], 'Succeed')
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(len(res.json()['messages']), 1)

        assetName = 'computer'
        ageLimit = 4
        numberLimit = 2

        res = self.put_asset_warning_assetName(assetName, ageLimit, numberLimit)
        self.assertEqual(res.json()['info'], 'Succeed')
        self.assertEqual(res.json()['code'], 0)

        res = self.get_asset_warning_message()
        self.assertEqual(res.json()['info'], 'Succeed')
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(len(res.json()['messages']), 2)
        
        assetName = 'computer'
        ageLimit = 4
        numberLimit = 4

        res = self.put_asset_warning_assetName(assetName, ageLimit, numberLimit)
        self.assertEqual(res.json()['info'], 'Succeed')
        self.assertEqual(res.json()['code'], 0)

        res = self.get_asset_warning_message()
        self.assertEqual(res.json()['info'], 'Succeed')
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(len(res.json()['messages']), 3)

        res = self.delete_asset_warning_assetName(assetName)
        self.assertEqual(res.json()['info'], 'Succeed')
        self.assertEqual(res.json()['code'], 0)

        res = self.get_asset_warning_message()
        self.assertEqual(res.json()['info'], 'Succeed')
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(len(res.json()['messages']), 1)

        res = self.get_asset_warning_assetName(assetName)
        self.assertEqual(res.json()['code'], 2)

        assetName = 'keyboard'
        res = self.get_asset_warning_assetName(assetName)
        self.assertEqual(res.json()['info'], 'Succeed')
        self.assertEqual(res.json()['code'], 0)