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
from Asset.models import Attribute, Asset, AssetAttribute, AssetCategory
from .models import NormalRequests, TransferRequests

from eam_backend.settings import SECRET_KEY
import jwt

def subtree_department(department: Department):
    children_list = [department.id]
    children = department.get_children()
    for child in children:
        children_list += subtree_department(child)
    return children_list
# Create your views here.
@CheckRequire
def requests_return(req: HttpRequest):
    if req.method == 'POST':
        CheckAuthority(req, ["staff"])
        token, decoded = CheckToken(req)
        user = User.objects.filter(username=decoded['username']).first()
        body = json.loads(req.body.decode("utf-8"))
        assets_list = get_args(body, ["assets"], ["list"])[0]
        err_msg = ""
        for idx, asset_name in enumerate(assets_list):
            asset = Asset.objects.filter(entity=user.entity, name=asset_name).first()
            if asset is None:
                err_msg += f'第{idx+1}条想要退库的资产不存在；'
                continue
            if asset.state != 'IN_USE':
                err_msg += f'第{idx+1}条想要退库的资产不在使用中；'
                continue
            request = NormalRequests.objects.filter(initiator=user, asset=asset, type=2, result=0).first()
            if request is not None:
                err_msg += f'第{idx+1}条想要退库的资产已提交退库申请；'
                continue
            request = NormalRequests.objects.filter(initiator=user, asset=asset, type=3, result=0).first()
            if request is not None:
                err_msg += f'第{idx+1}条想要退库的资产已提交维修申请；'
                continue
            request = NormalRequests(initiator=user, asset=asset, type=2, result=0, request_time=get_timestamp(),review_time=0.0)
            request.save()
        if len(err_msg) > 0:
            return request_failed(1, err_msg[:-1], status_code=403)
        return request_success()
    return BAD_METHOD

@CheckRequire
def waiting_list(req: HttpRequest):
    if req.method == 'GET':
        CheckAuthority(req, ["entity_super", "asset_super"])
        token, decoded = CheckToken(req)
        user = User.objects.filter(username=decoded['username']).first()
        department_list = subtree_department(user.department)
        requests_list = NormalRequests.objects.filter(asset__department__id__in=department_list).filter(result=0)
        waitinglist = []
        for request in requests_list:
            waitinglist.append(return_field(request.serialize(), ["initiator", "asset", "type", "request_time"]))
        return request_success({
            "waiting": waitinglist
        })
    return BAD_METHOD

@CheckRequire
def requests_repair(req: HttpRequest):
    if req.method == 'POST':
        CheckAuthority(req, ["staff"])
        token, decoded = CheckToken(req)
        user = User.objects.filter(username=decoded['username']).first()
        body = json.loads(req.body.decode("utf-8"))
        assets_list = get_args(body, ["assets"], ["list"])[0]
        err_msg = ""
        for idx, asset_name in enumerate(assets_list):
            asset = Asset.objects.filter(entity=user.entity, name=asset_name).first()
            if asset is None:
                err_msg += f'第{idx+1}条想要维修的资产不存在；'
                continue
            if asset.state != 'IN_USE':
                err_msg += f'第{idx+1}条想要维修的资产不在使用中（只有在员工手中的资产才可被维修）；'
                continue
            request = NormalRequests.objects.filter(initiator=user, asset=asset, type=3, result=0).first()
            if request is not None:
                err_msg += f'第{idx+1}条想要维修的资产已提交维修申请；'
                continue
            request = NormalRequests.objects.filter(initiator=user, asset=asset, type=2, result=0).first()
            if request is not None:
                err_msg += f'第{idx+1}条想要维修的资产已提交退库申请；'
                continue
            request = NormalRequests(initiator=user, asset=asset, type=3, result=0, request_time=get_timestamp(),review_time=0.0)
            request.save()
        if len(err_msg) > 0:
            return request_failed(1, err_msg[:-1], status_code=403)
        return request_success()
    return BAD_METHOD

@CheckRequire
def request_transfer(req:HttpRequest):
    if req.method=='POST':
        CheckAuthority(req, ["staff"])
        token, decoded = CheckToken(req)
        user = User.objects.filter(username=decoded['username']).first()
        body = json.loads(req.body.decode("utf-8"))
        assets, to, position = get_args(body, ["assets", "to", "position"], ["list", "string", "string"])
        checklength(to[1], 0, 50, "to")
        checklength(position, 0, 100,"position")
        if to[1] == user.username:
            return request_failed(1, "不能转移给自己", status_code=403)
        err_msg = ""
        for idx, asset_name in enumerate(assets):
            asset = Asset.objects.filter(entity=user.entity, name=asset_name).first()
            if asset is None:
                err_msg += f'第{idx+1}条想要转移的资产 {asset_name} 不存在；'
                continue
            if asset.state != 'IN_USE':
                err_msg += f'第{idx+1}条想要维修的资产 {asset_name} 不在使用中（只有在员工手中的资产才可被转移）；'
                continue
            request = NormalRequests.objects.filter(initiator=user, asset=asset, type=3, result=0).first()
            if request is not None:
                err_msg += f'第{idx+1}条想要转移的资产 {asset_name} 已提交维修申请；'
                continue
            request = NormalRequests.objects.filter(initiator=user, asset=asset, type=2, result=0).first()
            if request is not None:
                err_msg += f'第{idx+1}条想要转移的资产 {asset_name} 已提交退库申请；'
                continue
            request = TransferRequests.objects.filter(initiator=user, asset=asset, type=4, result=0).first()
            if request is not None:
                err_msg += f'第{idx+1}条想要转移的资产 {asset_name} 已提交转移申请；'
                continue
            request = TransferRequests(initiator=user, asset=asset, type=4, result=0, request_time=get_timestamp(),review_time=0.0)
            request.save()
        if len(err_msg) > 0:
            return request_failed(1, err_msg[:-1], status_code=403)
        return request_success()
    return BAD_METHOD