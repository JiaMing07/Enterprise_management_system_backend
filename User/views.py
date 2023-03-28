import json
import hashlib
from django.http import HttpRequest, HttpResponse

from User.models import User
from Department.models import Department, Entity
from utils.utils_request import BAD_METHOD, request_failed, request_success, return_field
from utils.utils_require import MAX_CHAR_LENGTH, CheckRequire, require
from utils.utils_time import get_timestamp
from utils.utils_getbody import get_args
from eam_backend.settings import SECRET_KEY
import jwt

def check_for_user_data(body):
    password = ""
    user_name = ""
    password = require(body, "password", "string", err_msg="Missing or error type of [password]")
    user_name = require(body, "username", "string", err_msg="Missing or error type of [userName]")
    assert 0 < len(user_name) <= 50, "Bad length of [username]"
    
    assert 0 < len(password) <=50, "Bad length of [password]"
    
    return user_name, password

# Create your views here.
@CheckRequire
def startup(req: HttpRequest):
    return HttpResponse("Congratulations! You have successfully installed the requirements. Go ahead!")

@CheckRequire
def login_normal(req: HttpRequest):
    if req.method == "POST":
        body = json.loads(req.body.decode("utf-8"))
        user_name, password = check_for_user_data(body)
        user = User.objects.filter(username=user_name).first()
        if not user:
            return request_failed(2, "不存在该用户", status_code=404)
        if not user.active:
            return request_failed(3, "用户已锁定", status_code=403)
        else:
            md5 = hashlib.md5()
            md5.update(password.encode('utf-8'))
            password = md5.hexdigest()
            if user.check_password(password):
                if user.token == '':
                    user.token = user.generate_token()
                    user.save()
                    return request_success(data={'token': user.token})
                else:
                    return request_failed(1, "用户已登录", status_code=403)
            else:
                return request_failed(2, "密码不正确", status_code=401)
    else:
        return BAD_METHOD

@CheckRequire    
def user_add(req: HttpRequest):
    if req.method == 'POST':
        body = json.loads(req.body.decode("utf-8"))
        user_name, entity_name, department_name, authority, password  = get_args(body, ['name', 'entity', 'department', 'authority', 'password'], ['string','string','string','string','string'])
        user = User.objects.filter(username=user_name).first()
        is_system_super = False
        is_entity_super = False
        is_asset_super = False
        if user is not None:
            return request_failed(1, "用户名已存在", status_code=403)
        entity = Entity.objects.filter(name=entity_name).first()
        department = Department.objects.filter(name=department_name).first()
        if not entity:
            return request_failed(1, "企业实体不存在",status_code=403)
        if not department:
            return request_failed(1, "部门不存在",status_code=403)
        if authority == "system_super":
            user = User.objects.filter(system_super=True).first()
            if user is not None:
                return request_failed(2, "不可设置此权限",status_code=403)
            is_system_super = True
        elif authority == "entity_super":
            user = User.objects.filter(entity_super=True).first()
            if user is not None:
                return request_failed(2, "不可设置此权限",status_code=403)
            is_entity_super = True
        elif authority == "asset_super":
            user = User.objects.filter(asset_super=True).first()
            if user is not None:
                return request_failed(2, "不可设置此权限",status_code=403)
            is_asset_super = True
        md5 = hashlib.md5()
        md5.update(password.encode('utf-8'))
        pwd = md5.hexdigest()
        user = User(username=user_name, entity=entity, department=department, system_super = is_system_super, entity_super = is_entity_super, asset_super = is_asset_super, password=pwd)
        user.save()
        return request_success()
    else:
        return BAD_METHOD
    
@CheckRequire
def logout_normal(req: HttpRequest):
    if req.method == 'POST':
        body = json.loads(req.body.decode("utf-8"))
        user_name = get_args(body, ['username'], ['string'])
        username = user_name[0]
        user = User.objects.filter(username=username).first()
        if user is not None:
            if user.token != '':
                user.token = ''
                user.save()
                return request_success()
            else:
                return request_failed(1, "登出失败", status_code=403)
        else:
            return request_failed(1, "登出失败", status_code=403)
    else:
        return BAD_METHOD
    
@CheckRequire
def user_lock(req: HttpRequest):
    if req.method == 'POST':
        body = json.loads(req.body.decode("utf-8"))
        user_name = require(body, "username", "string", err_msg="Missing or error type of [username]")
        active = require(body, "active", "int", err_msg="Missing or error type of [active]")

        user = User.objects.filter(username=user_name).first()
        if user is None:
            return request_failed(1, "用户不存在", status_code=404)
        if active is 1:
            if user.active is True:
                return request_failed(2, "用户已解锁", status_code=400)
            user.active = True
        elif active is 0:
            if user.active is False:
                return request_failed(2, "用户已锁定", status_code=400)
            user.active = False
        else:
            return request_failed(-2, "无效请求", status_code=400)
        user.save()
        return request_success()
    else:
        return BAD_METHOD

@CheckRequire
def user_edit(req: HttpRequest):
    if req.method == 'POST':
        body = json.loads(req.body.decode("utf-8"))
        user_name, pwd, pwd_new, department_name, authority = get_args(body, ['name', 'password', 'new_password', 'department', 'authority'], ['string','string','string','string', 'string'])

        user = User.objects.filter(username=user_name).first()

        if user is None:
            return request_failed(1, "用户不存在", status_code=404)
        if not user.check_password(pwd):
            return request_failed(2, "密码不正确", status_code=401)
        
        # 有修改password的需求
        if pwd_new is not None:
            # check format
            pwd_new = require(body, "new_password", "string", err_msg="Missing or error type of [new password]")
            
            # encryption
            md5 = hashlib.md5()
            md5.update(pwd_new.encode('utf-8'))
            new_pwd = md5.hexdigest()

            # if same with old one
            if user.check_password(new_pwd):
                return request_failed(2, "与原密码相同", status_code=205)
            else:
                user.password = new_pwd

        # 有修改authority的需求
        if authority is not None:
            ### 目前未考虑各种管理员最多有多少人

            # check format
            if authority != ("system_super" or "entity_super" or "asset_super"):
                return request_failed(1, "身份不存在", status_code=403)
            # if same with old one
            if authority == user.check_authen():
                return request_failed(2, "新身份与原身份相同", status_code=205)
            # diff then change
            else:
                user.system_super, user.entity_super, user.asset_super = user.set_authen(authority=authority)

        # 有修改department的需求
        if department_name is not None:
            # check format
            department = Department.objects.filter(name=department_name).first()
            if not department:
                return request_failed(1, "部门不存在", status_code=403)
            # if same with old one
            if department_name == user.department:
                return request_failed(2, "与原部门相同", status_code=205)
            # diff then change
            else:
                user.department = department_name
        
        user.save()
        return request_success()
    
    else:
        return BAD_METHOD