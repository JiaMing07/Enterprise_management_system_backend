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

        # whether check asset_super
        if not user.is_asset_super:
            return request_failed(2, "只有资产管理员可添加属性", status_code=403)
        
        else:
            # get son department
            children_list = []
            children = depart.get_children()
            for child in children:
                children_list.append(child.sub_tree())

            if department != depart and department not in children_list:
                return request_failed(2, "没有添加该部门自定义属性的权限", status_code=403)

        # check format
        checklength(name, 0, 50, "atrribute_name")

        # filter whether exist
        attri = Attribute.objects.filter(name=name).first()
        if attri is not None:
            return request_failed(1, "自定义属性已存在", status_code=403)

        # save
        else:
            new_attri = Attribute(name=name, entity=user.entity, department=department)
            new_attri.save()
            return request_success()
   
    else:
        return BAD_METHOD
    
@CheckRequire    
def attribute_list(req: HttpRequest):
    if req.method == 'GET':
        department_name = json.loads(req.body.decode("utf-8")).get('department')

        CheckToken(req)
        token = req.COOKIES['token'] 
        decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user = User.objects.get(username=decoded['username'])

        get_department = Department.objects.get(entity=user.entity, name=department_name)

        # asset_super can see son depart
        if user.is_asset_super:
            children_list = []
            children = user.department.get_children()
            for child in children:
                children_list.append(child.sub_tree())

            if get_department != user.department and get_department not in children_list:
                return request_failed(1, "没有查看该部门自定义属性的权限", status_code=403)

        # others can see own depart
        else:
            if get_department != user.department:
                return request_failed(1, "没有查看该部门自定义属性的权限", status_code=403)
        
        # get list
        attributes = Attribute.objects.filter(entity=user.entity).filter(department=get_department)
        return_data = {
            "attributes": [
                return_field(attribute.serialize(), ["id", "name"])
            for attribute in attributes],
        }
        return request_success(return_data)

    else:
        return BAD_METHOD