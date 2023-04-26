import json
import hashlib
from django.http import HttpRequest, HttpResponse

from User.models import User, Menu
from Department.models import Department, Entity
from utils.utils_request import BAD_METHOD, request_failed, request_success, return_field
from utils.utils_require import MAX_CHAR_LENGTH, CheckRequire, require
from utils.utils_time import get_timestamp
from utils.utils_getbody import get_args
from utils.utils_checklength import checklength
from utils.utils_checkauthority import CheckAuthority, CheckToken
from eam_backend.settings import SECRET_KEY
from  utils.utils_startup import init_department, init_entity, add_menu, add_users,admin_user, add_category, add_asset, add_request
import jwt
from django.db.utils import IntegrityError, OperationalError

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
    try:  # 在数据表创建前调用会引发错误
        init_entity()
        init_department()
        admin_user()
        add_users()
        add_category()
        add_asset()
        add_request()
        # add_menu()
    except (OperationalError, IntegrityError):
        pass
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
                # if user.token == '':
                user.token = user.generate_token()
                user.save()
                return request_success(data={'token': user.token,
                                            'system_super':user.system_super, 
                                            'entity_super': user.entity_super,
                                            'asset_super': user.asset_super,
                                            'department': user.department.name,
                                            'entity': user.entity.name,
                                            'active': user.active})
                # else:
                #     return request_failed(1, "用户已登录", status_code=403)
            else:
                return request_failed(2, "密码不正确", status_code=401)
    else:
        return BAD_METHOD

@CheckRequire    
def user_add(req: HttpRequest):
    if req.method == 'POST':
        body = json.loads(req.body.decode("utf-8"))
        user_name, entity_name, department_name, authority, password  = get_args(body, ['name', 'entity', 'department', 'authority', 'password'], ['string','string','string','string','string'])
        checklength(user_name, 0, 50, "username")
        checklength(entity_name, 0, 50, "entity_name")
        checklength(department_name, -1, 30, "department_name")
        user = User.objects.filter(username=user_name).first()
        is_system_super = False
        is_entity_super = False
        is_asset_super = False
        if user is not None:
            return request_failed(1, "用户名已存在", status_code=403)
        entity = Entity.objects.filter(name=entity_name).first()
        if not entity:
            return request_failed(1, "企业实体不存在",status_code=403)
        if authority == "system_super":
            user = User.objects.filter(system_super=True).first()
            if user is not None:
                return request_failed(2, "不可设置此权限",status_code=403)
            is_system_super = True
        elif authority == "entity_super":
            CheckAuthority(req, ["system_super"])
            user = User.objects.filter(entity=entity).filter(entity_super=True).first()
            if user is not None:
                return request_failed(2, "不可设置此权限",status_code=403)
            department_name = entity_name
            is_entity_super = True
        elif authority == "asset_super":
            CheckAuthority(req, ["entity_super"])
            is_asset_super = True
        department = Department.objects.filter(entity=entity).filter(name=department_name).first()
        if not department:
            return request_failed(1, "部门不存在",status_code=403)
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
        user = req.user
        body = json.loads(req.body.decode("utf-8"))
        user_name = get_args(body, ['username'], ['string'])
        username = user_name[0]
        checklength(username, 0, 50, "username")
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
        CheckAuthority(req, ["entity_super"])
        body = json.loads(req.body.decode("utf-8"))
        user_name = require(body, "username", "string", err_msg="Missing or error type of [username]")
        active = require(body, "active", "int", err_msg="Missing or error type of [active]")
        checklength(user_name, 0, 50, "username")
        user = User.objects.filter(username=user_name).first()
        if user is None:
            return request_failed(1, "用户不存在", status_code=404)
        if active == 1:
            if user.active is True:
                return request_failed(2, "用户已解锁", status_code=400)
            user.active = True
        elif active == 0:
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
        user_name = json.loads(req.body.decode("utf-8")).get('username')
        password = json.loads(req.body.decode("utf-8")).get('password')
        department_name = json.loads(req.body.decode("utf-8")).get('department')
        authority = json.loads(req.body.decode("utf-8")).get('authority')

        user = User.objects.filter(username=user_name).first()

        if user is None:
            return request_failed(1, "用户不存在", status_code=404)
        # 有修改password的需求
        if password is not None:
            # check format
            password = require(body, "password", "string", err_msg="Missing or error type of [new password]")

            # encryption
            md5 = hashlib.md5()
            md5.update(password.encode('utf-8'))
            new_pwd = md5.hexdigest()

            # if same with old one
            if user.check_password(new_pwd):
                return request_failed(3, "与原密码相同", status_code=205)
            else:
                user.password = new_pwd

        # 有修改authority的需求
        if authority is not None:
            ### 目前未考虑各种管理员最多有多少人
            # system_super = 1, entity_super = 1/entity, asset_super = n, staff = n
            if authority == "entity_super":
                CheckAuthority(req, ["system_super"])
                user.department = Department.objects.filter(name=user.entity.name).first()
            else:
                if user.entity_super:
                    CheckAuthority(req, ["system_super", "entity_super"])
                else:
                    CheckAuthority(req, ["entity_super"])
            if authority == "system_super":
                return request_failed(5, "无法设置权限", status_code=403)
            # check format
            auth = ["entity_super", "asset_super", "staff"]
            if authority not in auth:
                return request_failed(1, "身份不存在", status_code=403)
            
            # if same with old one
            if authority == user.check_authen():
                return request_failed(3, "新身份与原身份相同", status_code=205)
            
            # check one entity_super
            if authority == "entity_super":
                has_entity = User.objects.filter(entity=user.entity).filter(entity_super=True).first()
                if has_entity:
                    return request_failed(4, "该企业已存在系统管理员", status_code=205)

            # diff then change
            user.system_super, user.entity_super, user.asset_super = user.set_authen(authority=authority)

        # 有修改department的需求
        if department_name is not None:
            # check format
            department = Department.objects.filter(name=department_name).filter(entity=user.entity).first()
            if not department:
                return request_failed(1, "部门不存在", status_code=403)
            # if same with old one
            if department_name == user.department.name:
                return request_failed(3, "与原部门相同", status_code=205)
            # diff then change
            else:
                user.department = department
        
        user.save()
        return request_success()
    else:
        return BAD_METHOD
    
@CheckRequire
def user_list(req: HttpRequest):
    if req.method == 'GET':
        entities = Entity.objects.all()
        user_list = []
        for entity in entities:
            users = User.objects.filter(entity=entity)
            for user in users:
                user_list.append(return_field(user.serialize(), ["username", "entity", "department", "active", "authority"]))
        return_data = {
            "users": user_list,
        }
        return request_success(return_data)
    else:
        return BAD_METHOD
    
@CheckRequire
def user_userName(req: HttpRequest, userName: any):
    idx = require({"userName": userName}, "userName", "string", err_msg="Bad param [userName]", err_code=-1)
    checklength(userName, 0, 50, "userName")

    if req.method == 'DELETE':
        CheckAuthority(req, ["entity_super"])
        user = User.objects.filter(username=userName).first()
        if user is None:
            return request_failed(1, "user not found", status_code=404)
        if user.system_super:
            return request_failed(2, "禁止删除超级管理员", status_code=403)
        user.delete()
        return request_success()
    else:
        return BAD_METHOD


@CheckRequire
def user_menu(req: HttpRequest):
    if req.method == 'POST':
        CheckAuthority(req, ["entity_super"])
        token = req.COOKIES['token'] 
        decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user: User = User.objects.get(username=decoded['username'])
        body = json.loads(req.body.decode("utf-8"))
        first, second, authority, url = get_args(body, ["first", "second", "authority", "url"], ["string", "string", "string", "string"])
        checklength(first, 0, 50, "first")
        checklength(second, -1, 50, "second")
        checklength(url, -1, 500, "url")
        authorities = ['entity_super', 'asset_super', 'staff']
        authority = authority.split('/')
        menu_entity = Menu.objects.filter(entity=user.entity)
        menu_base = Menu.objects.filter(entity=Entity.objects.filter(name='admin_entity').first())
        menus = menu_entity | menu_base
        if second == "":
            menu = menus.filter(first=first).filter(second=second).first()
            if menu is not None:
                return request_failed(1, "一级菜单已存在", status_code=403)
        else:
            menu = menus.filter(first=first).filter(second=second).first()
            if menu is not None:
                return request_failed(2, "二级菜单已存在", status_code=403)
                
        for au in authority:
            if au not in authorities:
                return request_failed(3, "权限不存在",status_code=403)
        menu = Menu(first=first, second=second, url=url, entity=user.entity)
        menu.entity_show, menu.asset_show, menu.staff_show = menu.set_authority(authority)
        menu.save()
        return request_success()
    elif req.method == 'GET':
        CheckToken(req)
        token = req.COOKIES['token'] 
        decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user = User.objects.filter(username=decoded['username']).first()
        if user is None:
            return request_failed(-6, "不存在对应的用户", status_code=403)
        if user.token != token:
            return request_failed(-6, "用户不在线", status_code=403)
        authority = user.check_authen()
        menus_entity = Menu.objects.filter(entity = user.entity).filter(second="")
        menus_base = Menu.objects.filter(entity = Entity.objects.filter(name='admin_entity').first()).filter(second="")
        menus_list = menus_entity | menus_base
        if authority == 'entity_super':
            menu_list = Menu.objects.filter(entity_show=True)
        elif authority == 'asset_super':
            menu_list = Menu.objects.filter(asset_show=True)
        elif authority == 'staff':
            menu_list = Menu.objects.filter(staff_show=True)
        return_data = {
            "menu": [menu.serialize() for menu in menu_list]
        }
        return request_success(return_data)
    elif req.method == 'DELETE':
        CheckAuthority(req, ["entity_super"])
        token, decoded = CheckToken(req)
        user = User.objects.get(username=decoded['username'])
        entity = user.entity
        entity_base = Entity.objects.filter(name='admin_entity').first()
        body = json.loads(req.body.decode("utf-8"))
        first, second= get_args(body, ["first", "second"], ["string", "string"])
        checklength(first, 0, 50, "first")
        checklength(second, -1, 50, "second")
        if second == "":
            menus_entity = Menu.objects.filter(entity=entity).filter(first=first).filter(second="")
            menus_base = Menu.objects.filter(entity=entity_base).filter(first=first).filter(second="")
            if menus_base:
                return request_failed(3, "不可删除初始一级菜单", status_code=403)
            menus = menus_entity
            if len(menus) == 0:
                return request_failed(1, "一级菜单不存在", status_code=403)
            menus = Menu.objects.filter(first=first)
            for menu in menus:
                menu.delete()
        else:
            menus_entity = Menu.objects.filter(entity=entity).filter(first=first).filter(second=second)
            menus_base = Menu.objects.filter(entity=entity_base).filter(first=first).filter(second=second)
            if menus_base:
                return request_failed(4, "不可删除初始二级菜单", status_code=403)
            menu = menus_entity
            if len(menu) == 0:
                return request_failed(2, "二级菜单不存在", status_code=403)
            menu = menu[0]
            menu.delete()
        return request_success()
    return BAD_METHOD

def department_user_list(req: HttpRequest):
    if req.method == 'GET':
        token, decoded = CheckToken(req)
        user = User.objects.filter(username=decoded['username']).first()
        users = User.objects.filter(entity=user.entity)
        departments = Department.objects.filter(entity=user.entity).order_by('name')
        users_list = []
        for department in departments:
            user_department =users.filter(department=department)
            if len(user_department)> 0:
                dic = {
                    "department": department.name,
                    "users": [return_field(user_d.serialize(), ["username"]) for user_d in user_department]
                }
                users_list.append(dic)
        return request_success({
            "users_list": users_list
        })
    return BAD_METHOD

@CheckRequire
def menu_list(req: HttpRequest):
    if req.method == 'GET':
        CheckAuthority(req, ["entity_super"])
        menu_list = Menu.objects.all()
        return_data = {
            "menu": [menu.serialize() for menu in menu_list]
        }
        return request_success(return_data)
    return BAD_METHOD