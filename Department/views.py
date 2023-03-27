from django.shortcuts import render
import json
from django.http import HttpRequest, HttpResponse

from User.models import User
from Department.models import Department, Entity
from utils.utils_request import BAD_METHOD, request_failed, request_success, return_field
from utils.utils_require import MAX_CHAR_LENGTH, CheckRequire, require
from utils.utils_time import get_timestamp
from utils.utils_getbody import get_args

# Create your views here.
@CheckRequire
def startup(req: HttpRequest):
    return HttpResponse("Congratulations! You have successfully installed the requirements. Go ahead!")
# Create your views here.

@CheckRequire
def add_entity(req: HttpRequest):
    if req.method == 'POST':
        body = json.loads(req.body.decode("utf-8"))
        entity_name = get_args(body, ["name"], ['string'])[0]
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
        entity = Entity.objects.filter(name = entity_name).first()
        parent = Department.objects.filter(name=parent_name).first()
        if parent_name == "":
            parent = Department.objects.filter(id=1).first()
        if entity is None:
            return request_failed(1, "企业实体不存在", status_code=403)
        if parent is None:
            return request_failed(1, "父部门不存在", status_code=403)
        department = Department.objects.filter(name=department_name).first()
        if department is not None:
            print(department.name)
            return request_failed(1, "该部门已存在", status_code=403)
        department = Department(name=department_name, entity=entity, parent=parent)
        department.save()
        return request_success()

    return BAD_METHOD

def entity_list(req: HttpRequest,entity_name:str):
    if req.method == 'GET':
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