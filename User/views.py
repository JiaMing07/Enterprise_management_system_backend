import json
import hashlib
import requests
import random
from django.http import HttpRequest, HttpResponse

from User.models import User, Menu, UserFeishu
from Department.models import Department, Entity, Log
from utils.utils_request import BAD_METHOD, request_failed, request_success, return_field
from utils.utils_require import MAX_CHAR_LENGTH, CheckRequire, require
from utils.utils_time import get_timestamp, get_date
from utils.utils_getbody import get_args
from utils.utils_checklength import checklength
from utils.utils_checkauthority import CheckAuthority, CheckToken
from utils.utils_feishu import *

from eam_backend.settings import SECRET_KEY
from utils.utils_startup import init_department, init_entity, add_menu, add_users,admin_user, add_category, add_asset, add_request
import jwt
from django.db.utils import IntegrityError, OperationalError
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
from Asset.models import *

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
        add_menu()
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
                log_info = f"用户{user.username} ({user.department.name}) 在 {get_date()} 登录"
                log = Log(log=log_info, type = 0, entity=user.entity)
                log.save()
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
        token = req.COOKIES['token']
        decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        creator = User.objects.filter(username=decoded['username']).first()
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
        log_info = f"用户{creator.username} ({creator.department.name}) 在 {get_date()} 新增用户 {user.username}"
        log = Log(log=log_info, type = 1, entity=user.entity)
        log.save()
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
        token, decoded = CheckToken(req)
        creator = User.objects.filter(username=decoded['username']).first()
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
        log_info = f"用户{creator.username} ({creator.department.name}) 在 {get_date()} 锁定用户 {user.username}"
        log = Log(log=log_info, type = 1,entity = user.entity)
        log.save()
        return request_success()
    else:
        return BAD_METHOD

    
@CheckRequire
def user_edit(req: HttpRequest):
    if req.method == 'POST':
        token, decoded = CheckToken(req)
        creator_name = decoded['username']
        creator = User.objects.filter(username=decoded['username']).first()
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
        log_info = f"用户{creator_name} ({creator.department.name}) 在 {get_date()} 修改用户（{user.username}）的信息"
        log = Log(log=log_info, type = 1, entity=user.entity)
        log.save()
        return request_success()
    else:
        return BAD_METHOD
    
@CheckRequire
def user_list_page(req: HttpRequest, page:int):
    if req.method == 'GET':
        token, decoded = CheckToken(req)
        user = User.objects.filter(username=decoded['username']).first()
        entity = user.entity
        all_users = User.objects.filter(entity=entity)
        page = int(page)
        length = len(all_users)
        user_list = []
        def get_dic(u):
            dic = return_field(u.serialize(), ["username", "department", "active", "authority"])
            return dic
        if page < 1 or (page != 1 and page > (length-1)/20 + 1):
            return request_failed(-1, "超出页数范围", 403)
        if length % 20 != 0:
            if page == int(length/20) + 1:
                for i in range(length - (page-1)*20):
                    user_list.append(get_dic(all_users[(int(page)-1)*20+i]))
            else:
                for i in range(20):
                    user_list.append(get_dic(all_users[(int(page)-1)*20+i]))
        else:
            for i in range(20):
                user_list.append(get_dic(all_users[(int(page)-1)*20+i]))
        return_data = {
            "users": user_list,
            "total_count": length
        }
        return request_success(return_data)
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
        assets = Asset.objects.filter(owner=user.username)
        asset_super = User.objects.filter(entity=user.entity, department=user.department, asset_super=True).first()
        if asset_super is None:
            asset_super = User.objects.filter(entity=user.entity, entity_super = True).first()
        for ass in assets:
            ass.owner = asset_super.username
            ass.state = 'IDLE'
            ass.operation = 'IDLE'
            ass.change_time = get_timestamp()
            ass.save()
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
        log_info = f"用户{user.username} ({user.department.name}) 在 {get_date()} 增加菜单 {menu.first} {menu.second}"
        log = Log(log=log_info, type = 1, entity=user.entity)
        log.save()
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
        menus_entity = Menu.objects.filter(entity = user.entity)
        menus_base = Menu.objects.filter(entity = Entity.objects.filter(name='admin_entity').first())
        menus_list = menus_entity | menus_base
        if authority == 'entity_super':
            menu_list = menus_list.filter(entity_show=True)
        elif authority == 'asset_super':
            menu_list = menus_list.filter(asset_show=True)
        elif authority == 'staff':
            menu_list = menus_list.filter(staff_show=True)
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
            menus_entity = Menu.objects.filter(entity=entity).filter(first=first, second=second)
            menus_base = Menu.objects.filter(entity=entity_base).filter(first=first, second=second)
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
        token, decoded = CheckToken(req)
        user = User.objects.filter(username=decoded['username']).first()
        menu_list = Menu.objects.filter(entity=user.entity)
        return_data = {
            "menu": [menu.serialize() for menu in menu_list]
        }
        return request_success(return_data)
    return BAD_METHOD

@CheckRequire
def feishu_bind(req: HttpRequest):

    if req.method == 'POST':
        body = json.loads(req.body.decode("utf-8"))
        username = json.loads(req.body.decode("utf-8")).get('username')
        mobile = json.loads(req.body.decode("utf-8")).get('mobile')
        # open_id = json.loads(req.body.decode("utf-8")).get('open_id')
        # user_id = json.loads(req.body.decode("utf-8")).get('user_id')
        user = User.objects.filter(username=username).first()

        if user is None:
            return request_failed(2, "用户不存在", 403)
        
        oldbind = UserFeishu.objects.filter(username=username).first()
        user_id = get_user_id(mobile)
        print(f"user_id={user_id}")
        open_id = get_open_id(mobile)
        print(f"open_id={open_id}")

        # 如果已经绑定，则直接替换
        if oldbind is not None:
            oldbind.mobile = mobile
            oldbind.open_id = open_id
            oldbind.user_id = user_id
            oldbind.save()
        
        # 如果没有绑定，新建绑定
        else:
            userbind = UserFeishu(username=username, mobile=mobile, open_id=open_id, user_id=user_id)
            userbind.save()
        
        return request_success()
    
    elif req.method == 'GET':
        token, decoded = CheckToken(req)
        user = User.objects.filter(username=decoded['username']).first()
        
        if user is not None:
            userbind = UserFeishu.objects.filter(username=user.username).first()

            if userbind is None:
                return request_failed(1, "用户未绑定飞书账户", 403)
            
            mobile = userbind.mobile
            open_id = userbind.open_id
            user_id = userbind.user_id

            return_data = {
                "mobile": mobile,
                "open_id": open_id,
                "user_id": user_id
            }
            
            return request_success(return_data)

    return BAD_METHOD

@CheckRequire
def feishu_login(req: HttpRequest):

    if req.method == 'POST':
        body = json.loads(req.body.decode("utf-8"))
        code = json.loads(req.body.decode("utf-8")).get('code')

        # token, decoded = CheckToken(req)

        url = "https://passport.feishu.cn/suite/passport/oauth/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "grant_type": "authorization_code",
            "client_id": "cli_a4d212cbb87a500d",
            "client_secret": "M81ME3LFvgI7T0cIApC7xyTMuNEqbHFy",
            "code": code,
            "redirect_uri": "https://eam-frontend-bughunters.app.secoder.net/feishu"
            # "redirect_uri": "http://127.0.0.1:8000/feishu"
        }
        response = requests.post(url, headers=headers, data=data)
        # content_type = response.headers.get("Content-Type")
        # print("Content-Type:", content_type)

        if response.status_code == 200:
            json_data = response.json()
            access_token = json_data.get('access_token')
            token_type = json_data.get('token_type')
            expires_in = json_data.get('expires_in')
            refresh_token = json_data.get('refresh_token')
            refresh_expires_in = json_data.get('refresh_expires_in')
        
        else:
            return request_failed(2, "Failed to get response when requesting access_token", 403)

        # 构造请求Header
        headers = {
            "Authorization": f"Bearer {access_token}",
        }

        # 发送GET请求
        url = "https://passport.feishu.cn/suite/passport/oauth/userinfo"
        response = requests.get(url, headers=headers)

        # 获取返回的name参数
        if response.status_code == 200:
            data = response.json()
            # mobile的定义究竟是什么
            # mobile = data.get("name")
            mobile = data.get("mobile")
            print(mobile)
            open_id = data.get("open_id")
            feishuname = data.get("name")

            cur_bind = UserFeishu.objects.filter(mobile=mobile).first()
            print(cur_bind)
            if cur_bind is None:
                return request_failed(1, "Feishu not bind with any name.", 403)
            
            username = cur_bind.username
            cur_bind.open_id = open_id
            cur_bind.feishuname = feishuname
            user = User.objects.filter(username=username).first()
            
            if user is None:
                return request_failed(2, "User not exist.", 403)
            if not user.active:
                return request_failed(3, "用户已锁定", status_code=403)

            user.token = user.generate_token()
            user.save()

            return_data = {
                "username": username,
                "token": user.token,
                "system_super": user.system_super,
                "entity_super": user.entity_super,
                "asset_super": user.asset_super,
                "entity": user.entity.name,
                "department": user.department.name
            }
            return request_success(return_data)
            
        else:
            return request_failed(2, "Failed to get response when requesting userInfo.", 403)
        # print(json_data)

    return BAD_METHOD

@CheckRequire
def feishu_sync_click(req: HttpRequest):

    if req.method == 'POST':
        body = json.loads(req.body.decode("utf-8"))
        users = json.loads(req.body.decode("utf-8")).get('users')

        CheckAuthority(req, ["entity_super", "asset_super"])
        token, decoded = CheckToken(req)
        creator = User.objects.filter(username=decoded['username']).first()

        entity= creator.entity
        department = creator.department
        is_system_super = False
        is_entity_super = False
        is_asset_super = False

        # 检查每一个员工，如果open_id在userfeishu内存在object，不作操作
        for one in users:
            user_name = one["name"]
            open_id = one["open_id"]
            staff = UserFeishu.objects.filter(open_id=open_id)

            # 如果未绑定飞书账号
            if staff is None:
                # 如果飞书名和原有用户的用户名重复了
                user = User.objects.filter(username=user_name).first()
                while user is not None:
                    user_name = user_name + "OA"
                    user = User.objects.filter(username=user_name).first()
            
                # 初始密码都是000
                md5 = hashlib.md5()
                md5.update("000".encode('utf-8'))
                pwd = md5.hexdigest()
                    
                user = User(username=user_name, entity=entity, department=department, password=pwd,
                            system_super = is_system_super, entity_super = is_entity_super, asset_super = is_asset_super)
                user.save()
                
                log_info = f"用户{creator.username} ({creator.department.name}) 在 {get_date()} 新增用户 {user.username}"
                log = Log(log=log_info, type = 1, entity=user.entity)
                log.save()
        
        return request_success()
    return BAD_METHOD


# 每天10:30执行这个任务
# @register_job(scheduler, 'cron', id='feishu_sync', hour=10, minute=50, args=[])
def feishu_sync():
        
    # 创建entity
    entity = Entity.objects.filter(name="Ent_Feishu").first()
    if entity is None:
        # add entity
        entity = Entity(name="Ent_Feishu")
        entity.save()

        # add entity_super after sync

        # add root department
        department = Department(name="Ent_Feishu", entity=entity, parent=Department.root())
        department.save()
    
    # ent_super = User.objects.filter(entity=entity, entity_super=True).first()

    # user common info
    entity = Entity.objects.filter(name="Ent_Feishu").first()
    is_system_super = False
    is_entity_super = False
    is_asset_super = False
    
    ## 初始密码都是000
    md5 = hashlib.md5()
    md5.update("000".encode('utf-8'))
    pwd = md5.hexdigest()

    dep_list = get_dep_son(0)
    dep_name_list = [{"id": 0, "name": "Ent_Feishu"}]   # 记录id对应的部门名字，方便寻找父部门

    for dep in dep_list:
        depart_id = dep["department_id"]
        depart_name = dep["name"]
        dep_name_list.append({"id": depart_id, "name": depart_name})

        super_id = dep["leader_user_id"]

        depart_parent_id = dep["parent_department_id"]
        parent_name = ""
        for dep in dep_name_list:
            ## 应该父部门会先出现？
            if dep["id"] == depart_parent_id:
                parent_name = dep["name"]
                break

        # 创建部门

        ## 父部门是dep0
        if depart_parent_id == "0":
            parent_name = "Ent_Feishu"
            parent = Department.objects.filter(name="Ent_Feishu").first()
            if parent is None:
                parent = Department(name="Ent_Feishu", entity=entity, parent=Department.root())
                parent.save()

        ## 父部门不是dep0
        else:
            parent = Department.objects.filter(entity=entity).filter(name=parent_name).first()
            # 父部门不存在
            if parent is None:
                print("Should not be here!")
                parent = Department(name=parent_name, entity=entity)

            # 创建部门
            department = Department(name=depart_name, entity=entity, parent=parent)
            department.save()

            log_info = f"飞书用户{super_id}  在 {get_date()} 新增部门 {department.name}"
            log = Log(log=log_info, type = 1, entity=entity)
            log.save()

        # 添加users
        users = get_users(depart_id)
        super_name = ""
        for user in users:
            open_id = user["open_id"]
            user_id = user["user_id"]
            user_name = user["name"]
            mobile = user["mobile"]

            # 飞书名用户对应的原有用户是否存在
            staff = UserFeishu.objects.filter(open_id=open_id)

            # 如果未绑定飞书账号
            if staff is None:
                # 如果飞书名和原有用户的用户名重复了
                user = User.objects.filter(username=user_name).first()
            
                while user is not None:
                    random.seed()
                    user_name = user_name + random.randint(1, 100) # random 1~100
                    user = User.objects.filter(username=user_name).first()
                
                user = User(username=user_name, entity=entity, department=department, password=pwd,
                            system_super = is_system_super, entity_super = is_entity_super, asset_super = is_asset_super)
                
                if open_id == super_id:
                    super_name = user_name
                    user.asset_super = True
                
                user.save()

                log_info = f"用户{super_name} ({department.name}) 在 {get_date()} 新增用户 {user.username}"
                log = Log(log=log_info, type = 1, entity=user.entity)
                log.save()

                # 绑定
                oldbind = UserFeishu.objects.filter(username=user_name).first()
        
                userbind = UserFeishu(username=user_name, mobile=mobile, open_id=open_id, user_id=user_id)
                userbind.save()
    
    return request_success()

# 实例化调度器
scheduler = BackgroundScheduler()
# 调度器使用默认的DjangoJobStore()
scheduler.add_jobstore(DjangoJobStore(), 'default')

def test_add_task(request):
    if request.method == 'POST':
        content = json.loads(request.body.decode())  # 接收参数

        start_time = content['start_time']  # 用户输入的任务开始时间, '10:00:00'
        start_time = start_time.split(':')
        hour = int(start_time)[0]
        minute = int(start_time)[1]
        second = int(start_time)[2]
        # s = content['s']  # 接收执行任务的各种参数
        # 创建任务
        scheduler.add_job(feishu_sync, 'cron', hour=hour, minute=minute, second=second)
        
        return request_success()
    
# 注册定时任务并开始
register_events(scheduler)
scheduler.start()

@CheckRequire
def user_query(req: HttpRequest, description:str):
    if req.method == 'GET':
        token, decoded = CheckToken(req)
        description = str(description)
        user = User.objects.filter(username=decoded['username']).first()
        entity = user.entity
        users = User.objects.filter(entity=entity, entity_super=False, asset_super=False).filter(username__icontains=description)
        return_data = []
        for u in users:
            return_data.append({
                'username': u.username,
                'department': u.department.name
            })
        print(return_data)
        return request_success({
            'users': return_data
        })
    return BAD_METHOD 