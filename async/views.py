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
    print(i)
    print("in")
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