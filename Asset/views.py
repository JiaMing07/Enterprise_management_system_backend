from django.shortcuts import render
import json
from django.http import HttpRequest, HttpResponse

from utils.utils_request import BAD_METHOD, request_failed, request_success, return_field
from utils.utils_require import MAX_CHAR_LENGTH, CheckRequire, require
from utils.utils_time import get_timestamp
from utils.utils_getbody import get_args
from utils.utils_checklength import checklength
from utils.utils_checkauthority import CheckAuthority, CheckToken

from User.models import User
from Asset.models import AssetCategory, Asset, Attribute, AssetAttribute

# Create your views here.
@CheckRequire
def asset_category_list(req: HttpRequest):
    if req.method == 'GET':
        token, decoded = CheckToken(req)
        user = User.objects.filter(username=decoded['username']).first()
        entity = user.entity
        categories = AssetCategory.objects.filter(entity=entity)
        return_data = {
            "categories": [
                return_field(category.serialize(), ["id", "categoryName"])
            for category in categories],
        }
        return request_success(return_data)
    else:
        return BAD_METHOD
    
@CheckRequire
def asset_category_add(req: HttpRequest):
    if req.method == 'POST':
        CheckAuthority(req, ["entity_super"])
        body = json.loads(req.body.decode("utf-8"))
        name, parentName = get_args(body, ["name", "parent"], ["string", "string"])
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
        category = AssetCategory(name=name, entity=entity, parent=parent)
        category.save()
        return request_success()
    else:
        return BAD_METHOD
    
@CheckRequire
def asset_list(req: HttpRequest):
    if req.method == 'GET':
        token, decoded = CheckToken(req)
        user = User.objects.filter(username=decoded['username']).first()
        entity = user.entity
        assets = Asset.objects.filter(entity=entity)
        return_data = {
            "assets": [
                return_field(asset.serialize(), ["id", "assetName"])
            for asset in assets],
        }
        return request_success(return_data)
    else:
        return BAD_METHOD

@CheckRequire
def asset_add(req: HttpRequest):
    if req.method == 'POST':
        CheckAuthority(req, ["entity_super"])
        body = json.loads(req.body.decode("utf-8"))
        name, parentName, description, position, value, owner, is_number, number, categoryName = get_args(
            body, ["name", "parent", "description", "position", "value", "owner", "is_number", "number", "category"], 
            ["string", "string", "string", "string", "int", "string", "bool", "int", "string"])
        token, decoded = CheckToken(req)
        user = User.objects.filter(username=decoded['username']).first()
        entity = user.entity
        checklength(name, 0, 50, "assetName")
        checklength(parentName, -1, 50, "parentName")
        checklength(owner, 0, 50, "owner")
        checklength(categoryName, 0, 50, "categoryName")
        if parentName == "":
            parentName = entity.name
            parent = Asset.objects.filter(name=entity.name).first()
            if parent is None:
                parent = Asset(name=entity.name, owner=user.username, 
                               category=AssetCategory.root(), entity=entity, parent=Asset.root())
                parent.save()
        parent = Asset.objects.filter(entity=entity, name=parentName).first()
        if parent is None:
            return request_failed(1, "父资产不存在", status_code=404)
        category = AssetCategory.objects.filter(name=categoryName, entity=entity).first()
        if category is None:
            return request_failed(2, "资产类型不存在", status_code=404)
        owner_user = User.objects.filter(username=owner).first()
        if owner_user is None:
            return request_failed(3, "owner用户不存在", status_code=404)
        asset = Asset.objects.filter(entity=entity, name=name).first()
        if asset:
            return request_failed(4, "该资产已存在", status_code=403)
        asset = Asset(name=name, description=description, position=position, value=value, owner=owner, 
                      is_number=is_number, number=number, category=category, entity=entity, parent=parent)
        asset.save()
        return request_success()
    else:
        return BAD_METHOD