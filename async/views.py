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
        print(ans)
        return request_success()
    return BAD_METHOD

@CheckRequire
def show_list(req: HttpRequest):
    if req.method == 'GET':
        all = AsyncTask.objects.all()
        print(all)
        data = []
        for each in all:
            data.append(each.serialze())
        return request_success({
            'data': data
        })
    return BAD_METHOD