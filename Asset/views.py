from django.shortcuts import render
import json
from django.http import HttpRequest, HttpResponse

from utils.utils_request import BAD_METHOD, request_failed, request_success, return_field
from utils.utils_require import MAX_CHAR_LENGTH, CheckRequire, require
from utils.utils_time import get_timestamp
from utils.utils_getbody import get_args
from utils.utils_checklength import checklength
from utils.utils_checkauthority import CheckAuthority, CheckToken

from User.models import User, Menu
from Department.models import Department, Entity
from Asset.models import Attribute, Asset, AssetAttribute, AssetCategory

from eam_backend.settings import SECRET_KEY
import jwt

# Create your views here.
@CheckRequire
def asset_category_list(req: HttpRequest):
    print(req.COOKIES)
    if req.method == 'GET':
        token, decoded = CheckToken(req)
        user = User.objects.filter(username=decoded['username']).first()
        entity = user.entity
        category = AssetCategory.objects.filter(entity=entity).first()
        if category is None:
            return_data = {
                "categories": {},
            }
            return request_success(return_data)
        while True:
            parent = category.get_ancestors(ascending=True).first()
            if (parent is None or parent.entity != entity):
                break
            else:
                category = parent
        category_list = category.sub_tree()["sub-categories"]
        if len(category_list) == 0:
            return_data = {
                "categories": [],
            }
        else:
            return_data = {
                "categories": category_list,
            }
        return request_success(return_data)
    else:
        return BAD_METHOD
    
@CheckRequire
def asset_category_add(req: HttpRequest):
    print(req.COOKIES)
    if req.method == 'POST':
        CheckAuthority(req, ["entity_super", "asset_super"])
        body = json.loads(req.body.decode("utf-8"))
        name, parentName, is_number = get_args(body, ["name", "parent", "is_number"], ["string", "string", "bool"])
        token, decoded = CheckToken(req)
        user = User.objects.filter(username=decoded['username']).first()
        entity = user.entity
        checklength(name, 0, 50, "categoryName")
        checklength(parentName, -1, 50, "parentName")
        if parentName == "":
            parentName = entity.name
            parent = AssetCategory.objects.filter(name=entity.name).first()
            if parent is None:
                parent = AssetCategory(name=entity.name, entity=entity, parent=AssetCategory.root())
                parent.save()
        parent = AssetCategory.objects.filter(entity=entity, name=parentName).first()
        if parent is None:
            return request_failed(1, "父资产类型不存在", status_code=404)
        category = AssetCategory.objects.filter(entity=entity, name=name).first()
        if category:
            return request_failed(2, "该资产类型已存在", status_code=403)
        category = AssetCategory(name=name, entity=entity, parent=parent, is_number=is_number)
        category.save()
        return request_success()
    else:
        return BAD_METHOD
    
@CheckRequire
def asset_category_delete(req: HttpRequest):
    if req.method == 'DELETE':
        CheckAuthority(req, ["entity_super", "asset_super"])
        token, decoded = CheckToken(req)
        user = User.objects.filter(username=decoded['username']).first()
        entity = user.entity

        body = json.loads(req.body.decode("utf-8"))
        categoryName = body.get('categoryName')
        checklength(categoryName, 0, 50, "categoryName")

        category = AssetCategory.objects.filter(entity=entity, name=categoryName).first()
        if category is None:
            return request_failed(1, "category not found", status_code=404)
        
        category.delete()
        return request_success()
    else:
        return BAD_METHOD
    
@CheckRequire
def asset_list(req: HttpRequest):
    if req.method == 'GET':
        token, decoded = CheckToken(req)
        user = User.objects.filter(username=decoded['username']).first()
        entity = user.entity
        assets = Asset.objects.filter(entity=entity).exclude(name=entity.name).order_by('id')
        return_data = {
            "assets": [
                return_field(asset.serialize(), ["id", "assetName", "parentName", "category", "description", 
                                                 "position", "value", "user", "number", "state", "department", "image"])
            for asset in assets],
        }
        return request_success(return_data)
    else:
        return BAD_METHOD

@CheckRequire
def asset_add(req: HttpRequest):
    body = json.loads(req.body.decode("utf-8"))
    print(body)
    if req.method == 'POST':
        CheckAuthority(req, ["entity_super", "asset_super"])
        body = json.loads(req.body.decode("utf-8"))
        name, parentName, description, position, value, department, number, categoryName, image_url = get_args(
            body, ["name", "parent", "description", "position", "value", "department", "number", "category", "image"], 
            ["string", "string", "string", "string", "int", "string", "int", "string", "string"])
        token, decoded = CheckToken(req)
        user = User.objects.filter(username=decoded['username']).first()
        entity = user.entity
        checklength(name, 0, 50, "assetName")
        checklength(parentName, -1, 50, "parentName")
        checklength(department, -1, 30, "department")
        checklength(categoryName, 0, 50, "categoryName")
        checklength(description, 0, 300, "description")
        checklength(position, 0, 300, "position")
        checklength(image_url, -1, 300, "imageURL")
        print(f"d{department}")
        if parentName == "":
            parentName = entity.name
            parent = Asset.objects.filter(name=entity.name).first()
            if parent is None:
                parent = Asset(name=entity.name, owner=user.username, 
                               category=AssetCategory.root(), entity=entity, department=Department.objects.filter(entity=entity, name=entity.name).first(), parent=Asset.root())
                parent.save()
            if department == "":
                department = user.department
            else:
                department = Department.objects.filter(entity=entity, name=department).first()
                if department is None:
                    return request_failed(3, "挂账部门不存在", status_code=404)
        else:
            parent = Asset.objects.filter(entity=entity, name=parentName).first()
            if parent is None:
                return request_failed(1, "父资产不存在", status_code=404)
            department = parent.department
        category = AssetCategory.objects.filter(name=categoryName, entity=entity).first()
        if category is None:
            return request_failed(2, "资产类型不存在", status_code=404)
        asset = Asset.objects.filter(entity=entity, name=name).first()
        if asset:
            return request_failed(4, "该资产已存在", status_code=403)
        owner = User.objects.filter(entity=entity, department=department, asset_super=True).first()
        if owner is None:
            return request_failed(5, "部门不存在资产管理员",status_code=404)
        ancestor_list = department.get_ancestors(include_self=True)
        if user.department not in ancestor_list:
            return request_failed(5, "部门不在管理范围内", status_code=403)
        asset = Asset(name=name, description=description, position=position, value=value, owner=owner, number=number,
                      category=category, entity=entity, department=department, parent=parent, image_url=image_url)
        asset.save()
        return request_success()
    else:
        return BAD_METHOD
    
@CheckRequire
def asset_delete(req: HttpRequest):
    if req.method == 'DELETE':
        CheckAuthority(req, ["entity_super", "asset_super"])
        token, decoded = CheckToken(req)
        user = User.objects.filter(username=decoded['username']).first()
        entity = user.entity

        body = json.loads(req.body.decode("utf-8"))
        assetName = body.get('assetName')
        checklength(assetName, 0, 50, "assetName")

        asset = Asset.objects.filter(entity=entity, name=assetName).first()
        if asset is None:
            return request_failed(1, "asset not found", status_code=404)
        
        department = asset.department
        ancestor_list = department.get_ancestors(include_self=True)
        if user.department not in ancestor_list:
            return request_failed(2, "部门不在管理范围内", status_code=403)
        
        asset.delete()
        return request_success()
    else:
        return BAD_METHOD

@CheckRequire    
def attribute_add(req: HttpRequest):
    if req.method == 'POST':
        name = json.loads(req.body.decode("utf-8")).get('name')
        department_name = json.loads(req.body.decode("utf-8")).get('department')

        CheckToken(req)
        token = req.COOKIES['token'] 
        decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user = User.objects.get(username=decoded['username'])
        department = Department.objects.get(entity=user.entity, name=department_name)
        depart = user.department
        if user.token != token:
            return request_failed(-6, "用户不在线", status_code=403)

        # whether check asset_super and entity_super
        if user.asset_super:
            # get son department
            children_list = depart.get_children()

            if department != depart and department not in children_list:
                return request_failed(2, "没有添加该部门自定义属性的权限", status_code=403)
        
        if not user.entity_super and not user.asset_super:
            return request_failed(2, "只有资产管理员可添加属性", status_code=403)
            
        # check format
        checklength(name, 0, 50, "atrribute_name")

        # filter whether exist
        attri = Attribute.objects.filter(name=name).first()
        if attri is not None:
            return request_failed(1, "自定义属性已存在", status_code=403)
        
        # save
        new_attri = Attribute(name=name, entity=user.entity, department=department)
        new_attri.save()
        return request_success()
   
    else:
        return BAD_METHOD
    
@CheckRequire    
def attribute_list(req: HttpRequest, department: any):
    if req.method == 'GET':
        idx = require({"department": department}, "department", "string", err_msg="Bad param [department]", err_code=-1)
        checklength(department, 0, 50, "department_name")

        CheckToken(req)
        token = req.COOKIES['token'] 
        decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user = User.objects.get(username=decoded['username'])
        
        # get list
        attributes = Attribute.objects.filter(entity=user.entity)
        return_data = {
            "attributes": [
                return_field(attribute.serialize(), ["id", "name"])
            for attribute in attributes],
        }
        return request_success(return_data)

    else:
        return BAD_METHOD
    
@CheckRequire    
def attribute_delete(req: HttpRequest):
    
    if req.method == 'DELETE':
        attribute_name = json.loads(req.body.decode("utf-8")).get('name')
        department_name = json.loads(req.body.decode("utf-8")).get('department')

        CheckToken(req)
        token = req.COOKIES['token'] 
        decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user = User.objects.get(username=decoded['username'])

        department = Department.objects.filter(entity=user.entity, name=department_name).first()
        attribute = Attribute.objects.filter(entity=user.entity, department=department, name=attribute_name).first()

        # get list
        if attribute is None:
            return request_failed(1, "该部门不存在该自定义属性", status_code=403)
        if department is None:
            return request_failed(1, "该企业不存在该部门", status_code=403)
        
        # entity_super can edit all deps in entity
        if user.entity_super:
            attribute.delete()
            return request_success()
            
        # asset_super can see son depart
        elif user.asset_super:
            children_list = user.department.get_children()

            if department != user.department and department not in children_list:
                return request_failed(2, "没有删除该部门自定义属性的权限", status_code=403)
            
            attribute.delete()
            return request_success()

        # others can see own depart
        else:
            return request_failed(2, "没有删除该部门自定义属性的权限", status_code=403)

    else:
        return BAD_METHOD
    
@CheckRequire    
def asset_attribute(req: HttpRequest):

    if req.method == 'POST':
        # check format
        body = json.loads(req.body.decode("utf-8"))
        asset_name, attribute_name, description = get_args(body, ['asset', 'attribute', 'description'], ['string','string','string'])
        checklength(asset_name, 0, 50, "asset")
        checklength(attribute_name, 0, 50, "attribute")
        checklength(description, 0, 300, "description")

        # check token and get entity
        CheckToken(req)
        token = req.COOKIES['token'] 
        decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user = User.objects.get(username=decoded['username'])
    
        if user.token != token:
            return request_failed(-6, "用户不在线", status_code=403)

        # whether check asset_super
        if not user.asset_super:
            return request_failed(2, "只有资产管理员可为资产添加属性", status_code=403)
        
        # get asset and attribute
        asset = Asset.objects.filter(entity=user.entity, name=asset_name).first()
        attribute = Attribute.objects.filter(name=attribute_name, entity=user.entity, department=user.department).first()

        # filter whether exist
        if asset is None:
            return request_failed(1, "资产不存在", status_code=403)
        if attribute is None:
            return request_failed(1, "自定义属性不存在", status_code=403)

        # save
        else:
            new_pair = AssetAttribute(asset=asset, attribute=attribute, description=description)
            new_pair.save()
            return request_success()

    else:
        return BAD_METHOD
    
@CheckRequire    
def asset_assetName(req: HttpRequest, assetName: str):
    if req.method == 'GET':
        token, decoded = CheckToken(req)
        user = User.objects.filter(username=decoded['username']).first()
        entity = user.entity

        checklength(assetName, 0, 50, 'assetName')
        asset = Asset.objects.filter(entity=entity, name=assetName).first()
        if asset is None:
            return request_failed(1, "asset not found", status_code=404)
        
        property = asset.serialize()
        assetAttributes = AssetAttribute.objects.filter(asset=asset)
        for assetAttribute in assetAttributes:
            property[assetAttribute.attribute.name] = assetAttribute.description
        return_data = {
            "property": property,
        }
        return request_success(return_data)
    else:
        return BAD_METHOD

@CheckRequire
def asset_tree(req: HttpRequest):
    if req.method == 'GET':
        token, decoded = CheckToken(req)
        user = User.objects.filter(username=decoded['username']).first()
        entity = user.entity
        department = user.department
        asset = Asset.objects.filter(entity=entity)
        def subtree_department(department):
            children_list = [department.id]
            children = department.get_children()
            for child in children:
                children_list += subtree_department(child)
            return children_list
        department_tree = subtree_department(department)
        assets = asset.filter(department__id__in=department_tree)
        assets_list = []
        for ass in assets:
            if ass.parent == None:
                break
            if ass.parent.name == entity.name:
                assets_list.append(ass)
        return_list = []
        for ass in assets_list:
            return_list.append(ass.sub_tree())
        return_data = {
            "assets": return_list
        }
        return request_success(return_data)
    return BAD_METHOD

@CheckRequire
def asset_category_number(req: HttpRequest, category_name: str):
    if req.method == 'GET':
        print(1)
        token, decoded = CheckToken(req)
        user = User.objects.filter(username=decoded['username']).first()
        category = AssetCategory.objects.filter(entity=user.entity, name=category_name).first()
        if category is None:
            return request_failed(1, "不存在此资产", status_code=404)
        is_number = category.is_number
        return request_success({
            "is_number": is_number
        })
    else:
        return BAD_METHOD