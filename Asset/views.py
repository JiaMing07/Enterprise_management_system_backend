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
            parent = AssetCategory.objects.filter(name=entity.name, entity=entity).first()
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
def asset_category_edit(req: HttpRequest):
    if req.method == 'PUT':
        CheckAuthority(req, ["entity_super", "asset_super"])
        body = json.loads(req.body.decode("utf-8"))
        oldName, categoryName, parentName, is_number = get_args(body, ["oldName", "name", "parent", "is_number"], 
                                                             ["string", "string", "string", "bool"])
        token, decoded = CheckToken(req)
        user = User.objects.filter(username=decoded['username']).first()
        entity = user.entity
        checklength(oldName, 0, 50, "oldCategoryName")
        checklength(categoryName, 0, 50, "CategoryName")
        checklength(parentName, -1, 50, "parentName")

        category = AssetCategory.objects.filter(name=oldName, entity=entity).first()
        if category is None:
            return request_failed(1, "旧资产类型不存在", status_code=404)
        
        category_2 = AssetCategory.objects.filter(name=categoryName, entity=entity).first()
        if category_2 and category_2.id != category.id:
            return request_failed(2, "新资产类型已存在", status_code=403)
        
        if parentName == "":
            parentName = entity.name
            parent = AssetCategory.objects.filter(name=entity.name, entity=entity).first()
            if parent is None:
                parent = AssetCategory(name=entity.name, entity=entity, parent=AssetCategory.root())
                parent.save()
        parent = AssetCategory.objects.filter(entity=entity, name=parentName).first()
        if parent is None:
            return request_failed(3, "父资产类型不存在", status_code=404)
        
        category.name = categoryName
        category.parent = parent
        category.is_number = is_number
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
        assets = assets.filter(state='IDLE')
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
        if parentName == "":
            parentName = entity.name
            parent = Asset.objects.filter(name=entity.name, entity=entity).first()
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
        asset = Asset(name=name, description=description, position=position, value=value, owner=owner.username, number=number,
                      category=category, entity=entity, department=department, parent=parent, image_url=image_url)
        asset.save()
        return request_success()
    else:
        return BAD_METHOD
    
@CheckRequire
def asset_edit(req: HttpRequest):
    if req.method == 'PUT':
        CheckAuthority(req, ["entity_super", "asset_super"])
        body = json.loads(req.body.decode("utf-8"))
        oldName, assetName, parentName, description, position, value, owner, number, state, categoryName, image_url = get_args(
            body, ["oldName", "name", "parent", "description", "position", "value", "owner", "number", "state", "category", "image"], 
            ["string", "string", "string", "string", "string", "int", "string", "int", "string", "string", "string"])
        token, decoded = CheckToken(req)
        user = User.objects.filter(username=decoded['username']).first()
        entity = user.entity
        checklength(oldName, 0, 50, "oldAssetName")
        checklength(assetName, 0, 50, "assetName")
        checklength(parentName, -1, 50, "parentName")
        checklength(categoryName, 0, 50, "categoryName")
        checklength(description, 0, 300, "description")
        checklength(position, 0, 300, "position")
        checklength(owner, 0, 50, "ownerName")
        checklength(state, 0, 50, "state")
        checklength(image_url, -1, 300, "imageURL")

        asset = Asset.objects.filter(name=oldName, entity=entity).first()
        if asset is None:
            return request_failed(1, "旧资产不存在", status_code=404)
        
        asset_2 = Asset.objects.filter(name=assetName, entity=entity).first()
        if asset_2 and asset_2.id != asset.id:
            return request_failed(2, "新资产名称已存在", status_code=403)
        
        category = AssetCategory.objects.filter(name=categoryName, entity=entity).first()
        if category is None:
            return request_failed(3, "资产类型不存在", status_code=404)
        
        owner_user = User.objects.filter(entity=entity, username=owner).first()
        if owner_user is None:
            return request_failed(4, "挂账人不存在",status_code=404)
        
        assetDepartment = asset.department
        ancestor_list = assetDepartment.get_ancestors(include_self=True)
        if user.department not in ancestor_list:
            return request_failed(5, "资产不在管理范围内", status_code=403)
        
        department = owner_user.department
        ancestor_list = department.get_ancestors(include_self=True)
        if user.department not in ancestor_list:
            return request_failed(6, "挂账人不在管理范围内", status_code=403)
        
        if parentName == "":
            parentName = entity.name
            parent = Asset.objects.filter(entity=entity, name=entity.name).first()
            if parent is None:
                parent = Asset(name=entity.name, owner=user.username, category=AssetCategory.root(), entity=entity, 
                               department=Department.objects.filter(entity=entity, name=entity.name).first(), parent=Asset.root())
                parent.save()
        parent = Asset.objects.filter(entity=entity, name=parentName).first()
        if parent is None:
            return request_failed(7, "父资产不存在", status_code=404)
        
        asset.name = assetName
        asset.parent = parent
        asset.description = description
        asset.position = position
        asset.value = value
        asset.owner = owner
        asset.number = number
        asset.state = state
        asset.category = category
        asset.department = department
        asset.image_url = image_url
        asset.save()
        return request_success()
    else:
        return BAD_METHOD
    
@CheckRequire
def asset_add_list(req:HttpRequest):
    if req.method == 'POST':
        CheckAuthority(req, ["entity_super", "asset_super"])
        body = json.loads(req.body.decode("utf-8"))
        assets_new = body['assets']
        token, decoded = CheckToken(req)
        user = User.objects.filter(username=decoded['username']).first()
        entity = user.entity
        err_msg=""
        print(assets_new)
        for idx, asset_single in enumerate(assets_new):
            print("yes")
            name, parentName, description, position, value, department, number, categoryName, image_url = get_args(
            asset_single, ["name", "parent", "description", "position", "value", "department", "number", "category", "image"], 
            ["string", "string", "string", "string", "int", "string", "int", "string", "string"])
            state = asset_single.get('state', 'IDLE')
            owner = asset_single.get('owner', "")
            checklength(name, 0, 50, "assetName")
            checklength(parentName, -1, 50, "parentName")
            checklength(department, -1, 30, "department")
            checklength(categoryName, 0, 50, "categoryName")
            checklength(description, 0, 300, "description")
            checklength(position, 0, 300, "position")
            checklength(image_url, -1, 300, "imageURL")
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
                        err_msg = err_msg +'第' +str(idx + 1) +"条资产录入失败，挂账部门不存在" + '；'
            else:
                parent = Asset.objects.filter(entity=entity, name=parentName).first()
                if parent is None:
                    err_msg = err_msg +'第' +str(idx + 1) +"条资产录入失败，父资产不存在" + '；'
                    continue
                if department == "":
                    department = parent.department
                else:
                    department = Department.objects.filter(entity=entity, name=department).first()
                    if department is None:
                        err_msg = err_msg +'第' +str(idx + 1) +"条资产录入失败，挂账部门不存在" + '；'
                        continue
            category = AssetCategory.objects.filter(name=categoryName, entity=entity).first()
            if category is None:
                err_msg = err_msg +'第' +str(idx + 1) +"条资产录入失败，资产类型不存在" + '；'
                continue
            asset = Asset.objects.filter(entity=entity, name=name).first()
            if asset:
                err_msg = err_msg +'第' +str(idx + 1) +"条资产录入失败，该资产已存在" + '；'
                continue
            if owner == "":
                owner = User.objects.filter(entity=entity, department=department, asset_super=True).first()
                if owner is None:
                    err_msg = err_msg +'第' +str(idx + 1) +"条资产录入失败，部门不存在资产管理员" + '；'
                    continue
            else:
                owner = User.objects.filter(entity=entity, department=department, username=owner).first()
                if owner is None:
                    err_msg = err_msg +'第' +str(idx + 1) +"条资产录入失败，挂账人不存在" + '；'
                    continue
            ancestor_list = department.get_ancestors(include_self=True)
            if user.department not in ancestor_list:
                err_msg = err_msg +'第' +str(idx + 1) +"条资产录入失败，部门不在管理范围内" + '；'
                continue
            asset = Asset(name=name, description=description, position=position, value=value, owner=owner.username, number=number,
                        category=category, entity=entity, department=department, parent=parent, image_url=image_url,state=state)
            asset.save()
        if len(err_msg)>0:
            return request_failed(1, err_msg[:-1], status_code=403)
        return request_success()
    return BAD_METHOD
    
@CheckRequire
def asset_retire(req: HttpRequest):
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
        
        asset.state = "RETIRED"
        asset.value = 0
        children_list = asset.get_children()
        for child in children_list:
            child.parent = Asset.objects.filter(name = asset.entity.name).first()
            child.save()
        asset.save()
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
        checklength(name, 0, 50, "attribute_name")

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
def attribute_edit(req: HttpRequest):
    
    if req.method == 'PUT':
        name = json.loads(req.body.decode("utf-8")).get('name')
        new_name = json.loads(req.body.decode("utf-8")).get('new_name')
        department_name = json.loads(req.body.decode("utf-8")).get('department')
        new_depart_name = json.loads(req.body.decode("utf-8")).get('new_depart')

        checklength(new_name, 0, 50, "attribute_name")

        CheckToken(req)
        token = req.COOKIES['token'] 
        decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user = User.objects.get(username=decoded['username'])

        department = Department.objects.filter(entity=user.entity, name=department_name).first()
        attribute = Attribute.objects.filter(entity=user.entity, department=department, name=name).first()

        # whether exist
        if department is None:
            return request_failed(1, "该企业不存在该部门", status_code=403)
        if attribute is None:
            return request_failed(1, "该部门不存在该自定义属性", status_code=403)
        
        # whether edit name:
        if new_name is not None:

            # whether same name
            new_attribute = Attribute.objects.filter(entity=user.entity, department=department, name=new_name).first()
            
            if new_depart_name is not None:
                new_depart = Department.objects.filter(entity=user.entity, name=new_depart_name).first()
                new_attribute = Attribute.objects.filter(entity=user.entity, department=new_depart, name=new_name).first()
            
            if new_attribute is not None and new_depart_name is not None:
                return request_failed(3, "新部门已存在该属性", status_code=403)
            
            if new_attribute is not None and new_depart_name is None:
                return request_failed(3, "当前部门已存在该属性", status_code=403)

            # entity_super can edit all deps in entity
            if user.entity_super:
                attribute.name = new_name
                
            # asset_super can see son depart
            elif user.asset_super:
                ancestor_list = department.get_ancestors()

                if department != user.department and user.department not in ancestor_list:
                    return request_failed(2, "没有修改该部门自定义属性名称的权限", status_code=403)
                
                attribute.name = new_name

            # others can see own depart
            else:
                return request_failed(2, "没有修改该部门自定义属性名称的权限", status_code=403)
            
        # whether edit department
        if new_depart_name is not None:

            # whether same name
            new_depart = Department.objects.filter(entity=user.entity, name=new_depart_name).first()
            new_attribute = Attribute.objects.filter(entity=user.entity, department=new_depart, name=attribute.name).first()
            if new_attribute is not None:
                return request_failed(3, "新部门已存在该属性", status_code=403)

            # entity_super can edit all deps in entity
            if user.entity_super:
                attribute.department = new_depart
                
            # asset_super can see son depart
            elif user.asset_super:
                children_list = user.department.get_children()

                if department != user.department and department not in children_list:
                    return request_failed(2, "没有修改该自定义属性部门的权限", status_code=403)
                
                attribute.department = new_depart

            # others can see own depart
            else:
                return request_failed(2, "没有修改该自定义属性部门的权限", status_code=403)
        
        attribute.save()
        return request_success()

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
        CheckAuthority(req, ["entity_super", "asset_super"])
        token = req.COOKIES['token'] 
        decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user = User.objects.get(username=decoded['username'])

        # get asset and attribute
        asset = Asset.objects.filter(entity=user.entity, name=asset_name).first()
        attribute = Attribute.objects.filter(name=attribute_name, entity=user.entity).first()

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

    if req.method == 'DELETE':
        body = json.loads(req.body.decode("utf-8"))
        asset_name, attribute_name = get_args(body, ['asset', 'attribute'], ['string','string'])
        checklength(asset_name, 0, 50, "asset")
        checklength(attribute_name, 0, 50, "attribute")
        
        # check token and get entity
        # CheckAuthority(req, ["entity_super", "asset_super"])
        token = req.COOKIES['token'] 
        decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user = User.objects.get(username=decoded['username'])

        if user.token != token:
            return request_failed(-6, "用户不在线", status_code=403)

        # whether
        if not user.asset_super and not user.entity_super:
            return request_failed(2, "没有删除资产属性的权限", status_code=403)
        
        # get asset and attribute
        asset = Asset.objects.filter(entity=user.entity, name=asset_name).first()
        attribute = Attribute.objects.filter(name=attribute_name, entity=user.entity).first()

        # filter whether exist
        if asset is None:
            return request_failed(1, "资产不存在", status_code=403)
        if attribute is None:
            return request_failed(1, "自定义属性不存在", status_code=403)
        
         # save
        old_pair = AssetAttribute.objects.filter(asset=asset, attribute=attribute).first()
        if old_pair is None:
            return request_failed(1, "资产没有该属性", status_code=403)
        
        old_pair.delete()
        return request_success()

    else:
        return BAD_METHOD
    
@CheckRequire
def asset_attribute_list(req: HttpRequest, assetName: any):
    
    if req.method == 'GET':
        
        idx = require({"asset": assetName}, "asset", "string", err_msg="Bad param [asset]", err_code=-1)
        checklength(assetName, 0, 50, "asset_name")
        
        token, decoded = CheckToken(req)
        user = User.objects.get(username=decoded['username'])

        asset = Asset.objects.filter(entity=user.entity, name=assetName).first()
        
        if asset is None:
            return request_failed(1, "企业不存在该资产", status_code=403)

        # whether check different authentication
        # # asset_super can see son depart
        # if user.asset_super:
        #     children_list = user.department.get_children()
        #     if get_department != user.department and get_department not in children_list:
        #         return request_failed(1, "没有查看该部门自定义属性的权限", status_code=403)

        # # others can see own depart
        # if not user.asset_super and not user.entity_super:
        #     if get_department != user.department:
        #         return request_failed(1, "没有查看该部门自定义属性的权限", status_code=403)
        
        # get list
        asset_attributes = AssetAttribute.objects.filter(asset=asset)
        aa_json = []
        for one in asset_attributes:
            dict_ = {}
            dict_['key'] = one.attribute.name
            dict_['value'] = one.description
            aa_json.append(dict_)

        return_data = {
            "attributes": aa_json,
        }
        return request_success(return_data)

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

def subtree_department(department: Department):
    children_list = [department.id]
    children = department.get_children()
    for child in children:
        children_list += subtree_department(child)
    return children_list

@CheckRequire
def asset_tree(req: HttpRequest):
    if req.method == 'GET':
        token, decoded = CheckToken(req)
        user = User.objects.filter(username=decoded['username']).first()
        entity = user.entity
        department = user.department
        asset = Asset.objects.filter(entity=entity)
        department_tree = subtree_department(department)
        assets = asset.filter(department__id__in=department_tree).filter(state='IDLE')
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
    
@CheckRequire
def asset_query(req: HttpRequest, type: str, description: str, attribute:str):
    if req.method == 'GET':
        token, decoded = CheckToken(req)
        user = User.objects.filter(username=decoded['username']).first()
        entity = user.entity
        attribute=attribute[:-1]
        description = description[:-1]
        if type == "asset_name":
            assets = Asset.objects.filter(name__icontains=description)
        elif type == "asset_description":
            assets = Asset.objects.filter(description__icontains=description)
        elif type == "asset_position":
            assets = Asset.objects.filter(position__icontains=description)
        elif type == "asset_type":
            assets = Asset.objects.filter(category__name__icontains=description)
        elif type == "asset_attribute":
            attribute_assets = AssetAttribute.objects.filter(description__icontains=description, attribute__name__icontains=attribute)
            asset = []
            for ass in attribute_assets:
                asset.append(ass.asset.id)
            assets = Asset.objects.filter(id__in=asset)
        elif type == "asset_status":
            assets = Asset.objects.filter(state__icontains=description)
        elif type == "asset_department":
            assets = Asset.objects.filter(department__name__icontains=description)
        elif type == "asset_owner":
            assets = Asset.objects.filter(owner__icontains=description)
        else:
            return request_failed(1, "此搜索类型不存在", status_code=403)
        assets = assets.filter(entity=entity).exclude(name=entity.name).order_by('id')
        department_tree = subtree_department(user.department)
        assets = assets.filter(department__id__in=department_tree)
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
def user_query(req: HttpRequest):
    if req.method=='GET':
        token, decoded = CheckToken(req)
        user = User.objects.filter(username=decoded['username']).first()
        assets = Asset.objects.filter(entity=user.entity, owner=user.username).exclude(name=user.entity.name)
        return_data = {
            "assets": [
                return_field(asset.serialize(), ["id", "assetName", "parentName", "category", "description", 
                                                 "position", "value", "user", "number", "state", "department", "image"])
            for asset in assets],
        }
        return request_success(return_data)
    return BAD_METHOD