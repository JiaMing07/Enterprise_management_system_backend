from django.shortcuts import render
import json
from django.http import HttpRequest, HttpResponse

from utils.utils_request import BAD_METHOD, request_failed, request_success, return_field
from utils.utils_require import MAX_CHAR_LENGTH, CheckRequire, require
from utils.utils_time import get_timestamp, get_date
from utils.utils_getbody import get_args
from utils.utils_checklength import checklength
from utils.utils_checkauthority import CheckAuthority, CheckToken

from User.models import User, Menu
from Department.models import Department, Entity
from Asset.models import Attribute, Asset, AssetAttribute, AssetCategory, Label

from .tasks import *
from eam_backend.celery import app
from celery.result import AsyncResult

from django.utils import timezone
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler

from eam_backend.settings import SECRET_KEY
import jwt
import asyncio
from asgiref.sync import sync_to_async
import datetime

from .models import AsyncModel, AsyncTask

# Create your views here.



async def http_call_async(i):
    try:
        entity = await Entity.objects.all().afirst()
        asy = await AsyncModel.objects.acreate(initiator="Alice", start_time=get_date(), status = "STARTED", body = {}, entity= entity)
        print('ok')
        for num in range(6):
            await asyncio.sleep(1)
            print(num)
        asy.end_time = get_date()
        asy.status = 'SUCCESS'
        asy.result = 'ok'
        print('ok')
        await asy.asave()
    except Exception as e:
        print(e)

async def add_asset(assets_new, username):
    user = await User.objects.filter(username=username).afirst()
    entity = await Entity.objects.filter(id=user.entity_id).afirst()
    asy = await AsyncModel.objects.acreate(initiator=username, start_time=get_date(), status = "STARTED", body = {'assets_new': assets_new}, entity=entity)
    err_msg=""
    for idx, asset_single in enumerate(assets_new):
        try:
            try:
                name, parentName, description, position, value, department, number, categoryName, image_url = get_args(
                asset_single, ["name", "parent", "description", "position", "value", "department", "number", "category", "image"], 
                ["string", "string", "string", "string", "int", "string", "int", "string", "string"])
            except Exception as e:
                error_code = -2 if len(e.args) < 2 else e.args[1]
                err_msg = err_msg + '第' +str(idx + 1) +"条资产输入信息有误, " + e.args[0] + ";"  # Refer to below
                print(err_msg)
                continue
            print(name, parentName, description, position, value, department, number, categoryName, image_url)
            state = asset_single.get('state', 'IDLE')
            owner = asset_single.get('owner', "")
            def check_length(string, lowerbound, upperbound, name,err_msg):
                if lowerbound < len(string) <=upperbound:
                    err_msg += f"Bad length of [{name}]；"
            check_length(name, 0, 50, "assetName", err_msg)
            check_length(parentName, -1, 50, "parentName", err_msg)
            check_length(department, -1, 30, "department", err_msg)
            check_length(categoryName, 0, 50, "categoryName", err_msg)
            check_length(description, 0, 300, "description", err_msg)
            check_length(position, 0, 300, "position", err_msg)
            check_length(image_url, -1, 300, "imageURL", err_msg)
            if parentName == "":
                parentName = entity.name
                parent = await Asset.objects.filter(name=entity.name).afirst()
                if parent is None:
                    d = await Department.objects.filter(entity=entity, name=entity.name).afirst()
                    c = await AssetCategory.objects.filter(id=1).afirst()
                    p = await Asset.objects.filter(id=1).afirst()
                    parent = Asset(name=entity.name, owner=user.username, 
                                category=c, entity=entity, department=d, parent=p)
                    parent.asave()
                if department == "":
                    department = Department.objects.filter(id=user.department_id).afirst()
                else:
                    department = await Department.objects.filter(entity=entity, name=department).afirst()
                    if department is None:
                        err_msg = err_msg +'第' +str(idx + 1) +"条资产录入失败，挂账部门不存在" + '；'
            else:
                parent = await Asset.objects.filter(entity=entity, name=parentName).afirst()
                if parent is None:
                    err_msg = err_msg +'第' +str(idx + 1) +"条资产录入失败，父资产不存在" + '；'
                    continue
                if department == "":
                    department = Department.objects.filter(id=parent.department_id).afirst()
                else:
                    department = await Department.objects.filter(entity=entity, name=department).afirst()
                    if department is None:
                        err_msg = err_msg +'第' +str(idx + 1) +"条资产录入失败，挂账部门不存在" + '；'
                        continue
            category = await AssetCategory.objects.filter(name=categoryName, entity=entity).afirst()
            if category is None:
                err_msg = err_msg +'第' +str(idx + 1) +"条资产录入失败，资产类型不存在" + '；'
                continue
            asset = await Asset.objects.filter(entity=entity, name=name).afirst()
            if asset:
                err_msg = err_msg +'第' +str(idx + 1) +"条资产录入失败，该资产已存在" + '；'
                continue
            if owner == "":
                owner = await User.objects.filter(entity=entity, department=department, asset_super=True).afirst()
                if owner is None:
                    err_msg = err_msg +'第' +str(idx + 1) +"条资产录入失败，部门不存在资产管理员" + '；'
                    continue
            else:
                owner = await User.objects.filter(entity=entity, department=department, username=owner).afirst()
                if owner is None:
                    err_msg = err_msg +'第' +str(idx + 1) +"条资产录入失败，挂账人不存在" + '；'
                    continue
            ancestor_list = department.get_ancestors(include_self=True)
            flag = False
            async for ancestor in ancestor_list:
                if user.department_id == ancestor.id:
                    flag = True
                    break
            if flag == False:
                err_msg = err_msg +'第' +str(idx + 1) +"条资产录入失败，部门不在管理范围内" + '；'
                continue
            late = await Asset.objects.all().order_by('id').alast()
            owner_name = owner.username
            asset = Asset(name=name, description=description, position=position, value=value, owner=owner_name, number=number,
                        category=category, entity=entity, department=department, parent=parent, image_url=image_url,state=state)
            await asset.asave()
        except Exception as e:
            print(e)
            continue
    asy.end_time = get_date()
    asy.status = 'SUCCESS'
    asy.result = 'ok'
    if len(err_msg) > 0:
        asy.result = err_msg[:-1]
        asy.status = 'FAILED'
    await asy.asave()

async def test2(req: HttpRequest):
    if req.method == 'GET':
        loop = asyncio.get_event_loop()
        loop.create_task(http_call_async(1))
        res = {"code": 0, "info": 'Succeed'}
        return HttpResponse(json.dumps(res))
    res = {"code": -3, "info": 'bad method'}
    return HttpResponse(json.dumps(res))

@CheckRequire
def model_list(req: HttpRequest):
    if req.method == 'GET':
        CheckAuthority(req, ['entity_super'])
        token, decoded = CheckToken(req)
        user = User.objects.filter(username=decoded['username']).first()
        entity = user.entity
        models = AsyncModel.objects.filter(entity=entity)
        print(models)
        data = []
        for m in models:
            data.append(m.serialize())
        return request_success({
            'data': data
        })
    return BAD_METHOD


async def add(req: HttpRequest):
    if req.method == 'POST':
        try:
            token = req.COOKIES['token']
        except KeyError:
            return request_failed(-2, 'Token未给出',status_code=400)
        try:
            decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            decode = jwt.decode(token, SECRET_KEY, leeway=datetime.timedelta(days=3650), algorithms=['HS256'])
            user = await User.objects.filter(username=decode['username']).afirst()
            user.token = ''
            user.asave()
            return request_failed(-2, 'Token已过期',status_code=400)
        except jwt.InvalidTokenError:
            return request_failed(-2, 'Token不合法',status_code=400)
        user = await User.objects.filter(username=decoded['username']).afirst()
        if user is None:
            return request_failed(-2, "不存在对应的用户",status_code=400)
        if user.token != token:
            return request_failed(-2, "用户已在其他地方登录，请退出后重新登陆",status_code=400)
        have_authority = False
        for au in ['entity_super', 'asset_super']:
            if user.check_authen() == au:
                have_authority = True
        if have_authority == False:        
            return request_failed(-2, "没有操作权限",status_code=400)
        body = json.loads(req.body.decode("utf-8"))
        assets_new = body['assets']
        token, decoded = CheckToken(req)
        loop = asyncio.get_event_loop()
        loop.create_task(add_asset(assets_new, user.username))
        return request_success()
    return BAD_METHOD

@CheckRequire
def show_list(req: HttpRequest):
    if req.method == 'GET':
        # all = AsyncTask.objects.all()
        all = TaskResult.objects.all()
        print(all)
        data = []
        # for each in all:
            # data.append(each.serialze())
        for each in all:
            data.append({
                'id':each.task_id,
                'start_time': each.date_created,
                'end_time': each.date_done, 
                'result': each.result,
                'status': each.status,
                'initiator': 'Alice'
            })
        return request_success({
            'data': data
        })
    return BAD_METHOD

@CheckRequire
def failed_list(req: HttpRequest):
    if req.method == 'GET':
        CheckAuthority(req, ['entity_super'])
        token, decoded = CheckToken(req)
        user = User.objects.filter(username=decoded['username']).first()
        entity = user.entity
        models = AsyncModel.objects.filter(entity=entity, status='FAILED')
        data = []
        for m in models:
            data.append(m.serialize())
        return request_success({
            'data': data
        })
    return BAD_METHOD


async def restart(req:HttpRequest):
    if req.method == 'POST':
        try:
            token = req.COOKIES['token']
        except KeyError:
            return request_failed(-2, 'Token未给出',status_code=400)
        try:
            decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            decode = jwt.decode(token, SECRET_KEY, leeway=datetime.timedelta(days=3650), algorithms=['HS256'])
            user = await User.objects.filter(username=decode['username']).afirst()
            user.token = ''
            user.asave()
            return request_failed(-2, 'Token已过期',status_code=400)
        except jwt.InvalidTokenError:
            return request_failed(-2, 'Token不合法',status_code=400)
        user = await User.objects.filter(username=decoded['username']).afirst()
        if user is None:
            return request_failed(-2, "不存在对应的用户",status_code=400)
        if user.token != token:
            return request_failed(-2, "用户已在其他地方登录，请退出后重新登陆",status_code=400)
        have_authority = False
        for au in ['entity_super']:
            if user.check_authen() == au:
                have_authority = True
        if have_authority == False:        
            return request_failed(-2, "没有操作权限",status_code=400)
        body = json.loads(req.body.decode("utf-8"))
        id = body.get('id', 0)
        if id == 0:
            return request_failed(1, "请求体错误，不存在对应原始任务", status_code=403)
        task = await AsyncModel.objects.filter(id=id).afirst()
        if task is None:
            return request_failed(2, "不存在原始任务", status_code=403)
        task_body = json.load(task.body)
        assets_new = task_body['assets_new']
        loop = asyncio.get_event_loop()
        loop.create_task(add_asset(assets_new, user.username))
        return request_success()
    return BAD_METHOD