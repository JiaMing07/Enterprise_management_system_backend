from django.test import TestCase, Client
from Asset.models import AssetCategory, Asset, Attribute, AssetAttribute
from Department.models import Department, Entity
from User.models import User, Menu
import hashlib
from http import cookies

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
        User.objects.create(username='test_user', password=pwd, department=dep, entity=ent)
        
        category = AssetCategory.objects.create(name='cate', entity=ent)
        
        Asset.objects.create(name='ass', entity=ent, owner="test_user", category=category, department=dep, state='IDLE')
        Asset.objects.create(name='asset_1', entity=ent, owner='George', category=category, department=dep_child)
        Asset.objects.create(name='asset_2', entity=ent, owner='George', category=category, department=dep_child)
        Asset.objects.create(name='asset_3', entity=ent, owner='George', category=category, department=dep_child)
        Attribute.objects.create(id=1, name="attri_0", entity=ent, department=dep_ent)

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

    def post_request_return(self, asset_list):
        payload = {
            "assets": asset_list,
        }    
        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.post("/requests/return", data=payload, content_type="application/json")
    
    def get_request_waiting(self):
        return self.client.get("/requests/waiting")
    
    def get_request_user(self):
        return self.client.get("/requests/user")
    
    def post_request_repair(self, asset_list):
        payload = {
            "assets": asset_list,
        }    
        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.post("/requests/repair", data=payload, content_type="application/json")
    
    def post_request_transfer(self, asset_list, to, position):
        payload = {
            "assets": asset_list,
            "to": to,
            "position": position
        }    
        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.post("/requests/transfer", data=payload, content_type="application/json")
    
    def post_request_require(self, asset_list):
        payload = {
            "assets": asset_list,
        }    
        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.post("/requests/require", data=payload, content_type="application/json")
    
    def post_request_approve(self, assets_list, type_list):
        payload = {
            "assetName": assets_list,
            "type": type_list
        }    
        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.post("/requests/approve", data=payload, content_type="application/json")
    
    def post_request_disapprove(self, asset_list, type_list):
        payload = {
            "assetName": asset_list,
            "type": type_list
        }    
        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.post("/requests/disapprove", data=payload, content_type="application/json")

    def post_request_delete(self, asset_list, type_list):
        payload = {
            "assetName": asset_list,
            "type": type_list
        }    
        payload = {k: v for k, v in payload.items() if v is not None}
        return self.client.post("/requests/delete", data=payload, content_type="application/json")
    
    # start test

    def test_request_return(self):
        user = self.create_token('test_user', 'staff')
        asset_list = ["as"]
        res = self.post_request_return(asset_list)
        self.assertEqual(res.json()['info'], "第1条想要退库的资产 as 不存在")
        self.assertEqual(res.json()['code'], 1)

        asset_list = ["ass"]
        res = self.post_request_return(asset_list)
        self.assertEqual(res.json()['info'], "第1条想要退库的资产 ass 不在使用中")
        self.assertEqual(res.json()['code'], 1)

        assets = Asset.objects.all()
        for ass in assets:
            ass.state = "IN_USE"
            ass.save()
        
        asset_list = ["ass"]
        res = self.post_request_return(asset_list)
        self.assertEqual(res.json()['info'], "Succeed")
        self.assertEqual(res.json()['code'], 0)

        asset_list = ["ass", "asset_1"]
        res = self.post_request_return(asset_list)
        self.assertEqual(res.json()['info'], "第1条想要退库的资产 ass 已提交退库申请")
        self.assertEqual(res.json()['code'], 1)

        asset_list = ["asset_2"]
        res = self.post_request_repair(asset_list)
        self.assertEqual(res.json()['info'], "Succeed")
        self.assertEqual(res.json()['code'], 0)

        asset_list = ["asset_2"]
        res = self.post_request_return(asset_list)
        self.assertEqual(res.json()['info'], "第1条想要退库的资产 asset_2 已提交维修申请")
        self.assertEqual(res.json()['code'], 1)

        asset_list = ["asset_3"]
        to = ["dep_child", "Alice"]
        position = "position_1"
        res = self.post_request_transfer(asset_list, to, position)
        self.assertEqual(res.json()['info'], "Succeed")
        self.assertEqual(res.json()['code'], 0)

        asset_list = ["asset_3"]
        res = self.post_request_return(asset_list)
        self.assertEqual(res.json()['info'], "第1条想要退库的资产 asset_3 已提交转移申请")
        self.assertEqual(res.json()['code'], 1)
        
    def test_request_waiting(self):
        user = self.create_token('test_user', 'entity_super')

        res = self.get_request_waiting()
        self.assertEqual(res.json()['info'], 'Succeed')
        self.assertEqual(res.json()['code'], 0)

    def test_request_repair(self):
        user = self.create_token('test_user', 'staff')
        asset_list = ["as"]
        res = self.post_request_repair(asset_list)
        self.assertEqual(res.json()['info'], "第1条想要维修的资产 as 不存在")
        self.assertEqual(res.json()['code'], 1)

        asset_list = ["ass"]
        res = self.post_request_repair(asset_list)
        self.assertEqual(res.json()['info'], "第1条想要维修的资产 ass 不在使用中（只有在员工手中的资产才可被维修）")
        self.assertEqual(res.json()['code'], 1)

        assets = Asset.objects.all()
        for ass in assets:
            ass.state = "IN_USE"
            ass.save()
        
        asset_list = ["ass"]
        res = self.post_request_return(asset_list)
        self.assertEqual(res.json()['info'], "Succeed")
        self.assertEqual(res.json()['code'], 0)

        asset_list = ["ass", "asset_1"]
        res = self.post_request_repair(asset_list)
        self.assertEqual(res.json()['info'], "第1条想要维修的资产 ass 已提交退库申请")
        self.assertEqual(res.json()['code'], 1)

        asset_list = ["asset_2"]
        res = self.post_request_repair(asset_list)
        self.assertEqual(res.json()['info'], "Succeed")
        self.assertEqual(res.json()['code'], 0)

        asset_list = ["asset_2"]
        res = self.post_request_repair(asset_list)
        self.assertEqual(res.json()['info'], "第1条想要维修的资产 asset_2 已提交维修申请")
        self.assertEqual(res.json()['code'], 1)

        asset_list = ["asset_3"]
        to = ["dep_child", "Alice"]
        position = "position_1"
        res = self.post_request_transfer(asset_list, to, position)
        self.assertEqual(res.json()['info'], "Succeed")
        self.assertEqual(res.json()['code'], 0)

        asset_list = ["asset_3"]
        res = self.post_request_repair(asset_list)
        self.assertEqual(res.json()['info'], "第1条想要维修的资产 asset_3 已提交转移申请")
        self.assertEqual(res.json()['code'], 1)

    def test_request_repair(self):
        user = self.create_token('test_user', 'staff')
        asset_list = ["as"]
        to = ["dep_child", "test_user"]
        position = "position_1"
        res = self.post_request_transfer(asset_list, to, position)
        self.assertEqual(res.json()['info'], "不能转移给自己")
        self.assertEqual(res.json()['code'], 2)

        to = ["dep_child", "Bob"]
        res = self.post_request_transfer(asset_list, to, position)
        self.assertEqual(res.json()['info'], "想要转移到的员工不存在")
        self.assertEqual(res.json()['code'], 3)

        to = ["dep_child", "Alice"]
        res = self.post_request_transfer(asset_list, to, position)
        self.assertEqual(res.json()['info'], "第1条想要转移的资产 as 不存在")
        self.assertEqual(res.json()['code'], 1)

        asset_list = ["ass"]
        res = self.post_request_transfer(asset_list, to, position)
        self.assertEqual(res.json()['info'], "第1条想要维修的资产 ass 不在使用中（只有在员工手中的资产才可被转移）")
        self.assertEqual(res.json()['code'], 1)

        assets = Asset.objects.all()
        for ass in assets:
            ass.state = "IN_USE"
            ass.save()
        
        asset_list = ["ass"]
        res = self.post_request_return(asset_list)
        self.assertEqual(res.json()['info'], "Succeed")
        self.assertEqual(res.json()['code'], 0)

        asset_list = ["ass", "asset_1"]
        res = self.post_request_transfer(asset_list, to, position)
        self.assertEqual(res.json()['info'], "第1条想要转移的资产 ass 已提交退库申请")
        self.assertEqual(res.json()['code'], 1)

        asset_list = ["asset_2"]
        res = self.post_request_repair(asset_list)
        self.assertEqual(res.json()['info'], "Succeed")
        self.assertEqual(res.json()['code'], 0)

        asset_list = ["asset_2"]
        res = self.post_request_transfer(asset_list, to, position)
        self.assertEqual(res.json()['info'], "第1条想要转移的资产 asset_2 已提交维修申请")
        self.assertEqual(res.json()['code'], 1)

        asset_list = ["asset_3"]
        to = ["dep_child", "Alice"]
        position = "position_1"
        res = self.post_request_transfer(asset_list, to, position)
        self.assertEqual(res.json()['info'], "Succeed")
        self.assertEqual(res.json()['code'], 0)

        asset_list = ["asset_3"]
        res = self.post_request_transfer(asset_list, to, position)
        self.assertEqual(res.json()['info'], "第1条想要转移的资产 asset_3 已提交转移申请")
        self.assertEqual(res.json()['code'], 1)

    def test_request_require(self):
        user = self.create_token('test_user', 'staff')
        asset_list = ["as"]
        res = self.post_request_require(asset_list)
        self.assertEqual(res.json()['info'], "第1条想要申领的资产 as 不存在")
        self.assertEqual(res.json()['code'], 1)

        asset = Asset.objects.filter(name="asset_1").first()
        asset.state = 'IN_USE'
        asset.save()
        asset_list = ["asset_1"]
        res = self.post_request_require(asset_list)
        self.assertEqual(res.json()['info'], "第1条想要申领的资产 asset_1 不在闲置中")
        self.assertEqual(res.json()['code'], 1)

        assets = Asset.objects.all()
        for ass in assets:
            ass.state = "IDLE"
            ass.save()

        user = self.create_token('Alice', 'staff')
        
        asset_list = ["asset_1"]
        res = self.post_request_require(asset_list)
        self.assertEqual(res.json()['info'], "Succeed")
        self.assertEqual(res.json()['code'], 0)

        asset_list = ["ass", "asset_1"]
        res = self.post_request_require(asset_list)
        self.assertEqual(res.json()['info'], "第1条想要申领的资产 ass 不在可申领的范围内；第2条想要申领的资产 asset_1 已提交申领申请")
        self.assertEqual(res.json()['code'], 1)

    def test_request_waiting(self):
        user = self.create_token('test_user', 'staff')

        res = self.get_request_user()
        self.assertEqual(res.json()['info'], 'Succeed')
        self.assertEqual(res.json()['code'], 0)

    def test_request_approve(self):
        user = self.create_token('George', 'asset_super')
        user.system_super, user.entity_super, user.asset_super = user.set_authen("staff")
        user.save()

        # 申领
        asset = Asset.objects.filter(name="asset_1").first()
        asset.state = "IDLE"
        asset.save()
        asset_list = ["asset_1"]
        res = self.post_request_require(asset_list)
        self.assertEqual(res.json()['info'], "Succeed")
        self.assertEqual(res.json()['code'], 0)

        # 退库
        asset = Asset.objects.filter(name="ass").first()
        asset.state = "IN_USE"
        asset.save()
        asset_list = ["ass"]
        res = self.post_request_return(asset_list)
        self.assertEqual(res.json()['info'], "Succeed")
        self.assertEqual(res.json()['code'], 0)

        # 维修
        asset = Asset.objects.filter(name="asset_2").first()
        asset.state = "IN_USE"
        asset.save()
        asset_list = ["asset_2"]
        res = self.post_request_repair(asset_list)
        self.assertEqual(res.json()['info'], "Succeed")
        self.assertEqual(res.json()['code'], 0)

        # 转移
        # asset = Asset.objects.filter(name="asset_3").first()
        # asset.state = "IN_USE"
        # asset.save()
        # asset_list = ["asset_3"]
        # res = self.post_request_repair(asset_list)
        # self.assertEqual(res.json()['info'], "Succeed")
        # self.assertEqual(res.json()['code'], 0)

        user.system_super, user.entity_super, user.asset_super = user.set_authen("asset_super")
        user.save()

        # 同意申领, 1
        asset_list = ["asset_1"]
        type_list = ["1"]
        res = self.post_request_approve(asset_list, type_list)
        self.assertEqual(res.json()['info'], "Succeed")
        self.assertEqual(res.json()['code'], 0)

        # 同意退库, 2
        asset_list = ["ass"]
        type_list = ["2"]
        res = self.post_request_approve(asset_list, type_list)
        self.assertEqual(res.json()['info'], "Succeed")
        self.assertEqual(res.json()['code'], 0)
        
        # 同意维修, 3
        asset_list = ["asset_2"]
        type_list = ["3"]
        res = self.post_request_approve(asset_list, type_list)
        self.assertEqual(res.json()['info'], "Succeed")
        self.assertEqual(res.json()['code'], 0)

        # 同意转移, 4
        # asset_list = [""]
        # type_list = ["4"]
        # res = self.post_request_approve(asset_list, type_list)
        # self.assertEqual(res.json()['info'], "Succeed")
        # self.assertEqual(res.json()['code'], 0)

    def test_request_disapprove(self):
        user = self.create_token('George', 'asset_super')
        user.system_super, user.entity_super, user.asset_super = user.set_authen("staff")
        user.save()

        # 申领
        asset = Asset.objects.filter(name="asset_1").first()
        asset.state = "IDLE"
        asset.save()
        asset_list = ["asset_1"]
        res = self.post_request_require(asset_list)
        self.assertEqual(res.json()['info'], "Succeed")
        self.assertEqual(res.json()['code'], 0)

        # 退库
        asset = Asset.objects.filter(name="ass").first()
        asset.state = "IN_USE"
        asset.save()
        asset_list = ["ass"]
        res = self.post_request_return(asset_list)
        self.assertEqual(res.json()['info'], "Succeed")
        self.assertEqual(res.json()['code'], 0)

        # 维修
        asset = Asset.objects.filter(name="asset_2").first()
        asset.state = "IN_USE"
        asset.save()
        asset_list = ["asset_2"]
        res = self.post_request_repair(asset_list)
        self.assertEqual(res.json()['info'], "Succeed")
        self.assertEqual(res.json()['code'], 0)

        # 转移
        # asset = Asset.objects.filter(name="asset_3").first()
        # asset.state = "IN_USE"
        # asset.save()
        # asset_list = ["asset_3"]
        # res = self.post_request_repair(asset_list)
        # self.assertEqual(res.json()['info'], "Succeed")
        # self.assertEqual(res.json()['code'], 0)

        user.system_super, user.entity_super, user.asset_super = user.set_authen("asset_super")
        user.save()

        # 拒绝申领, 1
        asset_list = ["asset_1"]
        type_list = ["1"]
        res = self.post_request_disapprove(asset_list, type_list)
        self.assertEqual(res.json()['info'], "Succeed")
        self.assertEqual(res.json()['code'], 0)

        # 拒绝退库, 2
        asset_list = ["ass"]
        type_list = ["2"]
        res = self.post_request_disapprove(asset_list, type_list)
        self.assertEqual(res.json()['info'], "Succeed")
        self.assertEqual(res.json()['code'], 0)
        
        # 拒绝维修, 3
        asset_list = ["asset_2"]
        type_list = ["3"]
        res = self.post_request_disapprove(asset_list, type_list)
        self.assertEqual(res.json()['info'], "Succeed")
        self.assertEqual(res.json()['code'], 0)

        # 拒绝转移, 4
        # asset_list = [""]
        # type_list = ["4"]
        # res = self.post_request_approve(asset_list, type_list)
        # self.assertEqual(res.json()['info'], "Succeed")
        # self.assertEqual(res.json()['code'], 0)
    
    def test_request_delete(self):
        user = self.create_token('test_user', 'staff')
        # user.system_super, user.entity_super, user.asset_super = user.set_authen("staff")
        # user.save()

        # 申领
        asset = Asset.objects.filter(name="asset_1").first()
        asset.state = "IDLE"
        asset.save()
        asset_list = ["asset_1"]
        res = self.post_request_require(asset_list)
        self.assertEqual(res.json()['info'], "Succeed")
        self.assertEqual(res.json()['code'], 0)

        # 退库
        asset = Asset.objects.filter(name="ass").first()
        asset.state = "IN_USE"
        asset.save()
        asset_list = ["ass"]
        res = self.post_request_return(asset_list)
        self.assertEqual(res.json()['info'], "Succeed")
        self.assertEqual(res.json()['code'], 0)

        # 维修
        asset = Asset.objects.filter(name="asset_2").first()
        asset.state = "IN_USE"
        asset.save()
        asset_list = ["asset_2"]
        res = self.post_request_repair(asset_list)
        self.assertEqual(res.json()['info'], "Succeed")
        self.assertEqual(res.json()['code'], 0)

        # 转移
        # asset = Asset.objects.filter(name="asset_3").first()
        # asset.state = "IN_USE"
        # asset.save()
        # asset_list = ["asset_3"]
        # res = self.post_request_repair(asset_list)
        # self.assertEqual(res.json()['info'], "Succeed")
        # self.assertEqual(res.json()['code'], 0)

        # user.system_super, user.entity_super, user.asset_super = user.set_authen("asset_super")
        # user.save()

        # 撤回申领, 1
        asset_list = ["asset_1"]
        type_list = ["1"]
        res = self.post_request_delete(asset_list, type_list)
        self.assertEqual(res.json()['info'], "Succeed")
        self.assertEqual(res.json()['code'], 0)

        # 撤回退库, 2
        asset_list = ["ass"]
        type_list = ["2"]
        res = self.post_request_delete(asset_list, type_list)
        self.assertEqual(res.json()['info'], "Succeed")
        self.assertEqual(res.json()['code'], 0)
        
        # 撤回维修, 3
        asset_list = ["asset_2"]
        type_list = ["3"]
        res = self.post_request_delete(asset_list, type_list)
        self.assertEqual(res.json()['info'], "Succeed")
        self.assertEqual(res.json()['code'], 0)

        # 撤回转移, 4
        # asset_list = [""]
        # type_list = ["4"]
        # res = self.post_request_approve(asset_list, type_list)
        # self.assertEqual(res.json()['info'], "Succeed")
        # self.assertEqual(res.json()['code'], 0)