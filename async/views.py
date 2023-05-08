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
from Asset.models import Attribute, Asset, AssetAttribute, AssetCategory, Label

from .tasks import *
from eam_backend.celery import app
from celery.result import AsyncResult

from django.utils import timezone
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler

from eam_backend.settings import SECRET_KEY
import jwt

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
        all = TaskResult.objects.filter(status='FAILED')
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