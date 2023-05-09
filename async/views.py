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

from .models import AsyncModel, AsyncTask

# Create your views here.

@CheckRequire
def test(req: HttpRequest):
    if req.method == 'POST':
        body = json.loads(req.body.decode("utf-8"))
        username = get_args(body,["username"], ["string"])[0]
        ans = []
        print(username)
        for i in range(3):
            name = username + str(i)
            res = test1.delay(body, name)
            ans.append(res)
            print(res.id)
        print(ans)
        return request_success()
    return BAD_METHOD


async def http_call_async(i):
    try:
        asy = await AsyncModel.objects.acreate(initiator="Alice", start_time=get_date(), status = "STARTED", body = {})
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

async def add(assets_new, username):
    asy = await AsyncModel.objects.acreate(initiator="Alice", start_time=get_date(), status = "STARTED", body = {'assets_new': assets_new})
    user = await User.objects.filter(username=username).afirst()
    entity=user.entity
    err_msg=""
    for idx, asset_single in enumerate(assets_new):
        name, parentName, description, position, value, department, number, categoryName, image_url = get_args(
        asset_single, ["name", "parent", "description", "position", "value", "department", "number", "category", "image"], 
        ["string", "string", "string", "string", "int", "string", "int", "string", "string"])
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
                department = user.department
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
                department = parent.department
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
            if user.department.id == ancestor.id:
                flag = True
                break
        if flag == False:
            err_msg = err_msg +'第' +str(idx + 1) +"条资产录入失败，部门不在管理范围内" + '；'
            continue
        await Asset.objects.acreate(name=name, description=description, position=position, value=value, owner=owner.username, number=number,
                    category=category, entity=entity, department=department, parent=parent, image_url=image_url,state=state)
    asy.end_time = get_date()
    asy.status = 'SUCCESS'
    asy.result = 'ok'
    print('ok')
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
        models = AsyncModel.objects.all()
        print(models)
        data = []
        for m in models:
            data.append(m.serialize())
        return request_success({
            'data': data
        })
    return BAD_METHOD

@CheckRequire
def add(req: HttpRequest):
    if req.method == 'POST':
        CheckAuthority(req, ["entity_super", "asset_super"])
        body = json.loads(req.body.decode("utf-8"))
        assets_new = body['assets']
        token, decoded = CheckToken(req)
        user = User.objects.filter(username=decoded['username']).first()
        res = add_assets.delay(assets_new, user.username)
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
        # all = AsyncTask.objects.all()
        all = TaskResult.objects.filter(status='FAILURE')
        print(all)
        data = []
        # for each in all:
            # data.append(each.serialze())
        for each in all:
            data.append({
                'task_id':each.task_id,
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
def restart(req:HttpRequest):
    if req.method == 'POST':
        body = json.loads(req.body.decode("utf-8"))
        print(body)
        id = get_args(body, ["id"], ["string"])[0]
        task = AsyncTask.objects.filter(task_id=id).first()
        print(task)
        assets_new = json.loads(task.body)
        print(assets_new)
        token, decoded = CheckToken(req)
        user = User.objects.filter(username=decoded['username']).first()
        res = add_assets.delay(assets_new, user.username)
        return request_success()
    return BAD_METHOD