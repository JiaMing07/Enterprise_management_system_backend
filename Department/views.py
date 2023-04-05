from django.shortcuts import render
import json
from django.http import HttpRequest, HttpResponse

from User.models import User
from Department.models import Department, Entity
from utils.utils_request import BAD_METHOD, request_failed, request_success, return_field
from utils.utils_require import MAX_CHAR_LENGTH, CheckRequire, require
from utils.utils_time import get_timestamp
from utils.utils_getbody import get_args
from utils.utils_checklength import checklength
from utils.utils_checkauthority import CheckAuthority, CheckToken

@CheckRequire
def add_entity(req: HttpRequest):
    if req.method == 'POST':
        CheckAuthority(req, "system_super")
        body = json.loads(req.body.decode("utf-8"))
        entity_name = get_args(body, ["name"], ['string'])[0]
        checklength(entity_name, 0, 50, "entity_name")
        entity = Entity.objects.filter(name=entity_name).first()
        if entity is not None:
            return request_failed(1, "企业实体已存在", status_code=403)
        entity = Entity(name=entity_name)
        entity.save()
        department = Department(name=entity_name, entity=entity, parent=Department.root())
        department.save()
        return request_success() 
    return BAD_METHOD

@CheckRequire
def add_department(req: HttpRequest):
    if req.method == 'POST':
        CheckAuthority(req, "entity_super")
        body = json.loads(req.body.decode("utf-8"))
        entity_name, department_name, parent_name = get_args(body, ["entity", "department", "parent"], ["string", "string", "string"])
        checklength(entity_name, 0, 50, "entity_name")
        checklength(department_name, 0, 30, "department_name")
        checklength(parent_name, -1, 30, "parent_name")
        entity = Entity.objects.filter(name = entity_name).first()
        if entity is None:
            return request_failed(1, "企业实体不存在", status_code=403)
        if parent_name == "":
            parent_name = entity_name
            parent = Department.objects.filter(name=entity_name).first()
            if parent is None:
                parent = Department(name=entity_name, entity=entity, parent=Department.root())
                parent.save()
        parent = Department.objects.filter(entity=entity).filter(name=parent_name).first()
        if parent is None:
            return request_failed(1, "父部门不存在", status_code=403)
        department = Department.objects.filter(entity=entity).filter(name=department_name).first()
        if department is not None:
            return request_failed(1, "该部门已存在", status_code=403)
        department = Department(name=department_name, entity=entity, parent=parent)
        department.save()
        return request_success()

    return BAD_METHOD

@CheckRequire
def entity_list(req: HttpRequest):
    if req.method == 'GET':
        entities = Entity.objects.all()
        return_data = {
            "entities": [
                return_field(entity.serialize(), ["id", "name"])
            for entity in entities],
        }
        return request_success(return_data)
    else:
        return BAD_METHOD

@CheckRequire
def entity_entityName_department_list(req: HttpRequest, entityName: any):
    idx = require({"entityName": entityName}, "entityName", "string", err_msg="Bad param [entityName]", err_code=-1)
    checklength(entityName, 0, 50, "entityName")

    if req.method == 'GET':
        entity = Entity.objects.filter(name=entityName).first()
        if entity is None:
            return request_failed(1, "entity not found", status_code=404)
        
        department = Department.objects.filter(entity=entity).first()
        while True:
            parent = department.get_ancestors(ascending=True).first()
            if (parent is None or parent.entity != entity):
                break
            else:
                department = parent

        return_data = {
            "entityName": entityName,
            "departments": department.sub_tree(),
        }
        return request_success(return_data)

    else:
        return BAD_METHOD

@CheckRequire
def entity_entity_name_list(req: HttpRequest,entity_name: str):
    if req.method == 'GET':
        if not 0 < len(entity_name) <=50:
            return request_failed(-2, "Bad length of [entity_name]", status_code=400)
        entity = Entity.objects.filter(name=entity_name).first()
        if entity is not None:
            users = User.objects.filter(entity=entity)
            user_list = []
            for user in users:
                user_list.append(return_field(user.serialize(), ['username', 'department', 'active', 'authority']))
            return request_success({
                'name':entity_name,
                'user_list': user_list
            })
        else:
            return request_failed(-2, "企业实体不存在", status_code=403)
    return BAD_METHOD

@CheckRequire
def department_delete(req: HttpRequest):
    if req.method == 'DELETE':
        CheckAuthority(req, "entity_super")
        # check for correct format
        entity_name = json.loads(req.body.decode("utf-8")).get('entity')
        department_name = json.loads(req.body.decode("utf-8")).get('department')
        assert 0 < len(department_name) <= 30, "Bad length of [department_name]"
        assert 0 < len(entity_name) <= 50, "Bad length of [entity_name]"

        # filter entity
        entity = Entity.objects.filter(name=entity_name).first()
        if entity is None:
            return request_failed(1, "企业实体不存在", status_code=403)
        if entity.name == 'admin_entity':
            return request_failed(2, "不可删除超级管理员所在的企业实体", status_code=403)

        # filter department
        department_ = Department.objects.filter(entity=entity).filter(name=department_name).first()
        if department_ is None:
            return request_failed(1, "部门不存在", status_code=403)
        if department_.name == 'admin_department':
            return request_failed(2, "不可删除超级管理员所在的部门", status_code=403)
        
        # delete
        department_.delete()
        return request_success()

    else:
        return BAD_METHOD
@CheckRequire
def entity_delete(req: HttpRequest, entity_name: str):
    if req.method == 'DELETE':
        CheckAuthority(req, "system_super")
        checklength(entity_name,0, 50, "entity_name")
        entity = Entity.objects.filter(name=entity_name).first()
        if entity is None:
            return request_failed(1, "企业实体不存在", status_code=403)
        if entity.name == 'admin_entity':
            return request_failed(2, "不可删除超级管理员所在的企业实体", status_code=403)
        entity.delete()
        return request_success()
    else:
        return BAD_METHOD