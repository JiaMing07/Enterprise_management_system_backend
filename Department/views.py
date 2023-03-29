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

@CheckRequire
def add_entity(req: HttpRequest):
    if req.method == 'POST':
        body = json.loads(req.body.decode("utf-8"))
        entity_name = get_args(body, ["name"], ['string'])[0]
        checklength(entity_name, 0, 50, "entity_name")
        entity = Entity.objects.filter(name=entity_name).first()
        if entity is not None:
            return request_failed(1, "企业实体已存在", status_code=403)
        entity = Entity(name=entity_name)
        entity.save()
        return request_success() 
    return BAD_METHOD

@CheckRequire
def add_department(req: HttpRequest):
    if req.method == 'POST':
        body = json.loads(req.body.decode("utf-8"))
        entity_name, department_name, parent_name = get_args(body, ["entity", "department", "parent"], ["string", "string", "string"])
        checklength(entity_name, 0, 50, "entity_name")
        checklength(department_name, 0, 30, "department_name")
        checklength(parent_name, -1, 30, "parent_name")
        print(Entity.objects.filter(name='entity_2'))
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