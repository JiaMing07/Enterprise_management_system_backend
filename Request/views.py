from django.shortcuts import render
import json
from django.http import HttpRequest, HttpResponse

from utils.utils_request import BAD_METHOD, request_failed, request_success, return_field
from utils.utils_require import MAX_CHAR_LENGTH, CheckRequire, require
from utils.utils_time import get_timestamp, get_date
from utils.utils_getbody import get_args
from utils.utils_checklength import checklength
from utils.utils_checkauthority import CheckAuthority, CheckToken
from utils.utils_feishu import *

from User.models import User, Menu
from Department.models import Department, Entity, Log
from Asset.models import Attribute, Asset, AssetAttribute, AssetCategory
from .models import NormalRequests, TransferRequests

from eam_backend.settings import SECRET_KEY
import jwt
import asyncio

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
        ids = []
        msgs = []
        flag = False
        feishu_user = UserFeishu.objects.filter(username=user.username).first()
        if feishu_user is not None:
            flag = True
        for idx, asset_name in enumerate(assets_list):
            asset = Asset.objects.filter(entity=user.entity, name=asset_name).first()
            if asset is None:
                err_msg += f'第{idx+1}条想要退库的资产 {asset_name} 不存在；'
                continue
            if asset.state != 'IN_USE':
                err_msg += f'第{idx+1}条想要退库的资产 {asset_name} 不在使用中；'
                continue
            request = NormalRequests.objects.filter(initiator=user, asset=asset, type=2, result=0).first()
            if request is not None:
                err_msg += f'第{idx+1}条想要退库的资产 {asset_name} 已提交退库申请；'
                continue
            request = NormalRequests.objects.filter(initiator=user, asset=asset, type=3, result=0).first()
            if request is not None:
                err_msg += f'第{idx+1}条想要退库的资产 {asset_name} 已提交维修申请；'
                continue
            request = TransferRequests.objects.filter(initiator=user, asset=asset, type=4, result=0).first()
            if request is not None:
                err_msg += f'第{idx+1}条想要退库的资产 {asset_name} 已提交转移申请；'
                continue
            request = NormalRequests(initiator=user, asset=asset, type=2, result=0, request_time=get_timestamp(),review_time=0.0)
            request.save()
            msg = f"{user.username} 退库资产 {asset_name}"
            ids.append("1"+str(request.id) + "1")
            msgs.append(msg)
        if len(err_msg) > 0:
            return request_failed(1, err_msg[:-1], status_code=403)
        if flag:
            tenant = get_tenant()
            create_feishu_task(ids, user.username, msgs,tenant, "退库", "PENDING", request.request_time, 0)
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
            waitinglist.append(return_field(request.serialize(), ["id", "initiator", "asset", "type", "request_time", "review_time", "messages", "status"]))
        transfer_list = TransferRequests.objects.filter(asset__department__id__in=department_list).filter(result=0)
        for request in transfer_list:
            waitinglist.append(return_field(request.serialize(), ["id", "participant","initiator", "asset", "type", "request_time", "review_time", "messages", "status"]))
        return request_success({
            "requests": waitinglist
        })
    return BAD_METHOD

@CheckRequire
def requests_number(req: HttpRequest):
    if req.method == 'GET':
        CheckAuthority(req, ["entity_super", "asset_super"])
        token, decoded = CheckToken(req)
        user = User.objects.filter(username=decoded['username']).first()
        department_list = subtree_department(user.department)
        requests_list = NormalRequests.objects.filter(asset__department__id__in=department_list).filter(result=0)
        num = len(requests_list)
        transfer_list = TransferRequests.objects.filter(asset__department__id__in=department_list).filter(result=0)
        num = num + len(transfer_list)
        return request_success({
            "number": num
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
        ids = []
        msgs = []
        flag = False
        feishu_user = UserFeishu.objects.filter(username=user.username).first()
        if feishu_user is not None:
            flag = True
        for idx, asset_name in enumerate(assets_list):
            asset = Asset.objects.filter(entity=user.entity, name=asset_name).first()
            if asset is None:
                err_msg += f'第{idx+1}条想要维修的资产 {asset_name} 不存在；'
                continue
            if asset.state != 'IN_USE':
                err_msg += f'第{idx+1}条想要维修的资产 {asset_name} 不在使用中（只有在员工手中的资产才可被维修）；'
                continue
            request = NormalRequests.objects.filter(initiator=user, asset=asset, type=3, result=0).first()
            if request is not None:
                err_msg += f'第{idx+1}条想要维修的资产 {asset_name} 已提交维修申请；'
                continue
            request = NormalRequests.objects.filter(initiator=user, asset=asset, type=2, result=0).first()
            if request is not None:
                err_msg += f'第{idx+1}条想要维修的资产 {asset_name} 已提交退库申请；'
                continue
            request = TransferRequests.objects.filter(initiator=user, asset=asset, type=4, result=0).first()
            if request is not None:
                err_msg += f'第{idx+1}条想要维修的资产 {asset_name} 已提交转移申请；'
                continue
            request = NormalRequests(initiator=user, asset=asset, type=3, result=0, request_time=get_timestamp(),review_time=0.0)
            request.save()
            msg = f"{request.initiator.username} 维修资产 {asset_name}"
            ids.append("1"+str(request.id) + "1")
            msgs.append(msg)
        if len(err_msg) > 0:
            return request_failed(1, err_msg[:-1], status_code=403)
        if flag:
            tenant = get_tenant()
            create_feishu_task(ids, user.username, msgs,tenant, "维修", "PENDING", request.request_time, 0)
        return request_success()
    return BAD_METHOD

@CheckRequire
def request_transfer(req:HttpRequest):
    if req.method=='POST':
        CheckAuthority(req, ["staff"])
        token, decoded = CheckToken(req)
        user = User.objects.filter(username=decoded['username']).first()
        body = json.loads(req.body.decode("utf-8"))
        assets, to, position = get_args(body, ["assets", "to", "position"], ["list", "list", "string"])
        checklength(to[1], 0, 50, "to")
        checklength(position, 0, 100,"position")
        if to[1] == user.username:
            return request_failed(2, "不能转移给自己", status_code=403)
        participant = User.objects.filter(username=to[1]).first()
        if participant is None:
            return request_failed(3, "想要转移到的员工不存在", status_code=403)
        err_msg = ""
        ids=[]
        msgs = []
        flag = False
        feishu_user = UserFeishu.objects.filter(username=user.username).first()
        if feishu_user is not None:
            flag = True
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
            request = TransferRequests(initiator=user, asset=asset, type=4, result=0, request_time=get_timestamp(),review_time=0.0, participant=participant, position=position)
            request.save()
            msg = f"{user.username} 转移资产 {asset_name} 到 {participant.department.name} {participant.username}"
            ids.append("2"+str(request.id) + "2")
            msgs.append(msg)
            
        if len(err_msg) > 0:
            return request_failed(1, err_msg[:-1], status_code=403)
        if flag:
            tenant = get_tenant()
            create_feishu_task(ids, user.username, msgs,tenant, "转移", "PENDING", request.request_time, 0)
        return request_success()
    return BAD_METHOD

@CheckRequire
def requests_require(req: HttpRequest):
    '''
    申领资产
    '''
    if req.method == 'POST':
        CheckAuthority(req, ["staff"])
        token, decoded = CheckToken(req)
        user = User.objects.filter(username=decoded['username']).first()
        body = json.loads(req.body.decode("utf-8"))
        assets_list = get_args(body, ["assets"], ["list"])[0]
        err_msg = ""
        ids = []
        msgs = []
        flag = False
        feishu_user = UserFeishu.objects.filter(username=user.username).first()
        if feishu_user is not None:
            flag = True
        for idx, asset_name in enumerate(assets_list):
            asset = Asset.objects.filter(entity=user.entity, name=asset_name).first()
            if asset is None:
                err_msg += f'第{idx+1}条想要申领的资产 {asset_name} 不存在；'
                continue
            if asset.state != 'IDLE':
                err_msg += f'第{idx+1}条想要申领的资产 {asset_name} 不在闲置中；'
                continue
            department_list = subtree_department(user.department)
            flag = False
            for d in department_list:
                if d == asset.department.id:
                    flag = True
                    break
            if flag == False:
                err_msg += f'第{idx+1}条想要申领的资产 {asset_name} 不在可申领的范围内；'
                continue
            request = NormalRequests.objects.filter(initiator=user, asset=asset, type=1, result=0).first()
            if request is not None:
                err_msg += f'第{idx+1}条想要申领的资产 {asset_name} 已提交申领申请；'
                continue
            request = NormalRequests(initiator=user, asset=asset, type=1, result=0, request_time=get_timestamp(),review_time=0.0)
            request.save()
            msg = f"{user.username} 申领资产 {asset_name}"
            ids.append("1"+str(request.id) + "1")
            msgs.append(msg)
        if len(err_msg) > 0:
            return request_failed(1, err_msg[:-1], status_code=403)
        if flag:
            tenant = get_tenant()
            create_feishu_task(ids, user.username, msgs,tenant, "申领", "PENDING", request.request_time, 0)
        return request_success()
    return BAD_METHOD

@CheckRequire
def requests_user(req: HttpRequest):
    if req.method == 'GET':
        token, decoded = CheckToken(req)
        user = User.objects.filter(username=decoded['username']).first()
        normal_requests = NormalRequests.objects.filter(initiator=user)
        transfer_requests = TransferRequests.objects.filter(initiator=user)
        requestslist = []
        for request in normal_requests:
            requestslist.append(return_field(request.serialize(), ["id", "initiator", "asset", "type", "request_time", "review_time", "messages", "status"]))
        for request in transfer_requests:
            requestslist.append(return_field(request.serialize(), ["id", "initiator","participant", "asset", "type", "request_time", "review_time", "messages", "status"]))
        return request_success({
            "requests": requestslist
        })
    return BAD_METHOD

@CheckRequire
def requests_list(req: HttpRequest):
    if req.method == 'GET':
        CheckAuthority(req, ["entity_super", "asset_super"])
        token, decoded = CheckToken(req)
        user = User.objects.filter(username=decoded['username']).first()
        department_list = subtree_department(user.department)
        requests_list = NormalRequests.objects.filter(asset__department__id__in=department_list)
        all_list = []
        for request in requests_list:
            all_list.append(return_field(request.serialize(), ["id", "initiator", "asset", "type", "request_time", "review_time", "messages", "status"]))
        transfer_list = TransferRequests.objects.filter(asset__department__id__in=department_list)
        for request in transfer_list:
            all_list.append(return_field(request.serialize(), ["id", "participant","initiator", "asset", "type", "request_time", "review_time", "messages", "status"]))
        return request_success({
            "requests": all_list
        })
    return BAD_METHOD

@CheckRequire
def requests_approve(req: HttpRequest):
    if req.method == 'POST':
        CheckAuthority(req, ["asset_super", "entity_super"])
        token, decoded = CheckToken(req)
        user = User.objects.filter(username=decoded['username']).first()

        body = json.loads(req.body.decode("utf-8"))
        assets_list = get_args(body, ["assetName"], ["list"])[0]
        type_list = get_args(body, ["type"], ["list"])[0]

        # approve requests
        # - 从 waiting list 中进行相应的操作
        # -- 是否在waiting list中
        # -- 进行对应的操作
        # - 从request list中删除

        department_list = subtree_department(user.department)
        normal_list = NormalRequests.objects.filter(asset__department__id__in=department_list).filter(result=0)
        transfer_list = TransferRequests.objects.filter(asset__department__id__in=department_list).filter(result=0)
        
        err_msg = ""
        ids = []
        msgs = []
        for idx, (asset_name, type) in enumerate(zip(assets_list, type_list)):
            asset = Asset.objects.filter(entity=user.entity, name=asset_name).first()
            # if asset is None:
            #     err_msg += f'第{idx+1}条想要维修的资产 {asset_name} 不存在；'
            #     continue
            if type == "1":   # 申领
                request = NormalRequests.objects.filter(asset=asset, type=1, result=0).first()
                if request not in normal_list:
                    err_msg += f'第{idx+1}条想要申领的资产 {asset_name} 不在申请list中; '
                else:
                    asset.owner = request.initiator.username
                    asset.state = 'IN_USE'
                    asset.operation = 'IN_USE'
                    request.review_time = get_timestamp()
                    request.result = 1
                    request.save()
                    msg = f"{request.initiator.username} 申领资产 {asset_name}"
                    feishu_user = UserFeishu.objects.filter(username=request.initiator.username).first()
                    if feishu_user is not None:
                        ids.append("1"+str(request.id) + "1")
                        msgs.append(msg)
                    # log_info = f"用户{user.username} ({user.department.name}) 在 {get_date()} 同意 {request.initiator.username} 的申领请求 {asset.name}"
                    # log = Log(log=log_info, type = 1, entity=user.entity)
                    # log.save()

            elif type == "2": # 退库
                request = NormalRequests.objects.filter(asset=asset, type=2, result=0).first()
                if request not in normal_list:
                    err_msg += f'第{idx+1}条想要退库的资产 {asset_name} 不在申请list中; '
                else:
                    asset.state = 'IDLE'
                    asset.owner = user.username
                    asset.operation = 'IDLE'
                    request.review_time = get_timestamp()
                    request.result = 1
                    request.save()
                    msg = f"{request.initiator.username} 退库资产 {asset_name}"
                    feishu_user = UserFeishu.objects.filter(username=request.initiator.username).first()
                    if feishu_user is not None:
                        ids.append("1"+str(request.id) + "1")
                        msgs.append(msg)
                    # log_info = f"用户{user.username} ({user.department.name}) 在 {get_date()} 同意 {request.initiator.username} 的退库请求 {asset.name}"
                    # log = Log(log=log_info, type = 1, entity=user.entity)
                    # log.save()

            elif type == "3": # 维修
                request = NormalRequests.objects.filter(asset=asset, type=3, result=0).first()
                if request not in normal_list:
                    err_msg += f'第{idx+1}条想要维修的资产 {asset_name} 不在申请list中; '
                else:
                    asset.state = 'IN_MAINTAIN'
                    asset.operation = 'IN_MAINTAIN'
                    request.review_time = get_timestamp()
                    request.result = 1
                    request.save()
                    msg = f"{request.initiator.username} 维修资产 {asset_name}"
                    feishu_user = UserFeishu.objects.filter(username=request.initiator.username).first()
                    if feishu_user is not None:
                        ids.append("1"+str(request.id) + "1")
                        msgs.append(msg)
                    # log_info = f"用户{user.username} ({user.department.name}) 在 {get_date()} 同意 {request.initiator.username} 的维修请求 {asset.name}"
                    # log = Log(log=log_info, type = 1, entity=user.entity)
                    # log.save()

            elif type == "4": # 转移
                request = TransferRequests.objects.filter(asset=asset, type=4, result=0).first()
                if request not in transfer_list:
                    err_msg += f'第{idx+1}条想要转移的资产 {asset_name} 不在申请list中; '
                else:
                    asset.owner = request.participant.username
                    asset.position = request.position
                    asset.operation = 'MOVE'
                    request.review_time = get_timestamp()
                    request.result = 1
                    request.save()
                    msg = f"{request.initiator.username} 转移资产 {asset_name} 到 {request.participant.department.name} {request.participant.username}"
                    feishu_user = UserFeishu.objects.filter(username=request.initiator.username).first()
                    if feishu_user is not None:
                        ids.append("2"+str(request.id) + "2")
                        msgs.append(msg)
                    # log_info = f"用户{user.username} ({user.department.name}) 在 {get_date()} 同意 {request.initiator.username} 的转移请求：{asset.name}转移至{request.participant.username}（{request.participant.department.name}）"
                    # log = Log(log=log_info, type = 1, entity=user.entity)
                    # log.save()

            else:
                err_msg += f'第{idx+1}条想要处理的资产 {asset_name} 申请不符合要求; '

            asset.change_time = get_timestamp()
            asset.change_value = 0
            asset.save()

        if len(err_msg) > 0:
            return request_failed(1, err_msg[:-1], status_code=403)
        if len(ids)>0:
            tenant = get_tenant()
            create_feishu_task(ids, user.username, msgs,tenant, "审批完成", "APPROVED", request.request_time, request.review_time)

        return request_success()
    
    return BAD_METHOD

@CheckRequire
def requests_delete(req: HttpRequest):
    if req.method == 'POST':
        CheckAuthority(req, ["staff"])
        token, decoded = CheckToken(req)
        user = User.objects.filter(username=decoded['username']).first()

        body = json.loads(req.body.decode("utf-8"))
        assets_list = get_args(body, ["assetName"], ["list"])[0]
        type_list = get_args(body, ["type"], ["list"])[0]

        # user delete requests
        # just delete

        normal_list = NormalRequests.objects.filter(initiator=user)
        transfer_list = TransferRequests.objects.filter(initiator=user)

        err_msg = ""
        ids = []
        msgs = []
        for idx, (asset_name, type) in enumerate(zip(assets_list, type_list)):
            asset = Asset.objects.filter(entity=user.entity, name=asset_name).first()
            
            if type == "1":   # 申领
                request = NormalRequests.objects.filter(initiator=user, asset=asset, type=1, result=0).first()
                if request not in normal_list:
                    err_msg += f'第{idx+1}条想要申领的资产 {asset_name} 不在申请list中; '
                else:
                    request.result = 3
                    request.save()
                    msg = f"{request.initiator.username} 申领资产 {asset_name}"
                    feishu_user = UserFeishu.objects.filter(username=request.initiator.username).first()
                    if feishu_user is not None:
                        ids.append("1"+str(request.id) + "1")
                        msgs.append(msg)

            elif type == "2": # 退库
                request = NormalRequests.objects.filter(initiator=user, asset=asset, type=2, result=0).first()
                if request not in normal_list:
                    err_msg += f'第{idx+1}条想要退库的资产 {asset_name} 不在申请list中; '
                else:
                    request.result = 3
                    request.save()
                    msg = f"{request.initiator.username} 退库资产 {asset_name}"
                    feishu_user = UserFeishu.objects.filter(username=request.initiator.username).first()
                    if feishu_user is not None:
                        ids.append("1"+str(request.id) + "1")
                        msgs.append(msg)

            elif type == "3": # 维修
                request = NormalRequests.objects.filter(initiator=user, asset=asset, type=3, result=0).first()
                if request not in normal_list:
                    err_msg += f'第{idx+1}条想要维修的资产 {asset_name} 不在申请list中; '
                else:
                    request.result = 3
                    request.save()
                    msg = f"{request.initiator.username} 维修资产 {asset_name}"
                    feishu_user = UserFeishu.objects.filter(username=request.initiator.username).first()
                    if feishu_user is not None:
                        ids.append("1"+str(request.id) + "1")
                        msgs.append(msg)

            elif type == "4": # 转移
                request = TransferRequests.objects.filter(initiator=user, asset=asset, type=4, result=0).first()
                if request not in transfer_list:
                    err_msg += f'第{idx+1}条想要转移的资产 {asset_name} 不在申请list中; '
                else:
                    request.result = 3
                    request.save()
                    msg = f"{request.initiator.username} 转移资产 {asset_name} 到 {request.participant.department.name} {request.participant.username}"
                    feishu_user = UserFeishu.objects.filter(username=request.initiator.username).first()
                    if feishu_user is not None:
                        ids.append("2"+str(request.id) + "2")
                        msgs.append(msg)

            else:
                err_msg += f'第{idx+1}条想要处理的资产 {asset_name} 申请不符合要求; '

        if len(err_msg) > 0:
            return request_failed(1, err_msg[:-1], status_code=403)
        if len(ids) > 0:
            tenant = get_tenant()
            create_feishu_task(ids, user.username, msgs,tenant, "撤回申请", "DELETED", request.request_time, get_timestamp())
        return request_success()
    
    return BAD_METHOD

@CheckRequire
def requests_disapprove(req: HttpRequest):
    if req.method == 'POST':
        CheckAuthority(req, ["asset_super", "entity_super"])
        token, decoded = CheckToken(req)
        user = User.objects.filter(username=decoded['username']).first()

        body = json.loads(req.body.decode("utf-8"))
        assets_list = get_args(body, ["assetName"], ["list"])[0]
        type_list = get_args(body, ["type"], ["list"])[0]

        # disapprove requests
        # -- 是否在waiting list中
        # -- 进行对应的操作
        # -- result = 2

        department_list = subtree_department(user.department)
        normal_list = NormalRequests.objects.filter(asset__department__id__in=department_list).filter(result=0)
        transfer_list = TransferRequests.objects.filter(asset__department__id__in=department_list).filter(result=0)
        
        err_msg = ""
        ids = []
        msgs = []
        for idx, (asset_name, type) in enumerate(zip(assets_list, type_list)):
            asset = Asset.objects.filter(entity=user.entity, name=asset_name).first()
            # if asset is None:
            #     err_msg += f'第{idx+1}条想要维修的资产 {asset_name} 不存在；'
            #     continue
            if type == "1":   # 申领
                request = NormalRequests.objects.filter(asset=asset, type=1, result=0).first()
                if request not in normal_list:
                    err_msg += f'第{idx+1}条想要申领的资产 {asset_name} 不在申请list中; '
                else:
                    request.review_time = get_timestamp()
                    request.result = 2
                    request.save()
                    msg = f"{request.initiator.username} 申领资产 {asset_name}"
                    feishu_user = UserFeishu.objects.filter(username=request.initiator.username).first()
                    if feishu_user is not None:
                        ids.append("1"+str(request.id) + "1")
                        msgs.append(msg)
                    # log_info = f"用户{user.username} ({user.department.name}) 在 {get_date()} 拒绝 {request.initiator.username} 的申领请求 {asset.name}"
                    # log = Log(log=log_info, type = 1, entity=user.entity)
                    # log.save()

            elif type == "2": # 退库
                request = NormalRequests.objects.filter(asset=asset, type=2, result=0).first()
                if request not in normal_list:
                    err_msg += f'第{idx+1}条想要退库的资产 {asset_name} 不在申请list中; '
                else:
                    request.review_time = get_timestamp()
                    request.result = 2
                    request.save()
                    msg = f"{request.initiator.username} 退库资产 {asset_name}"
                    feishu_user = UserFeishu.objects.filter(username=request.initiator.username).first()
                    if feishu_user is not None:
                        ids.append("1"+str(request.id) + "1")
                        msgs.append(msg)
                    # log_info = f"用户{user.username} ({user.department.name}) 在 {get_date()} 拒绝 {request.initiator.username} 的退库请求 {asset.name}"
                    # log = Log(log=log_info, type = 1, entity=user.entity)
                    # log.save()

            elif type == "3": # 维修
                request = NormalRequests.objects.filter(asset=asset, type=3, result=0).first()
                if request not in normal_list:
                    err_msg += f'第{idx+1}条想要维修的资产 {asset_name} 不在申请list中; '
                else:
                    request.review_time = get_timestamp()
                    request.result = 2
                    request.save()
                    msg = f"{request.initiator.username} 维修资产 {asset_name}"
                    feishu_user = UserFeishu.objects.filter(username=request.initiator.username).first()
                    if feishu_user is not None:
                        ids.append("1"+str(request.id) + "1")
                        msgs.append(msg)
                    # log_info = f"用户{user.username} ({user.department.name}) 在 {get_date()} 拒绝 {request.initiator.username} 的维修请求 {asset.name}"
                    # log = Log(log=log_info, type = 1, entity=user.entity)
                    # log.save()

            elif type == "4": # 转移
                request = TransferRequests.objects.filter(asset=asset, type=4, result=0).first()
                if request not in transfer_list:
                    err_msg += f'第{idx+1}条想要转移的资产 {asset_name} 不在申请list中; '
                else:
                    request.review_time = get_timestamp()
                    request.result = 2
                    request.save()
                    msg = f"{request.initiator.username} 转移资产 {asset_name} 到 {request.participant.department.name} {request.participant.username}"
                    feishu_user = UserFeishu.objects.filter(username=request.initiator.username).first()
                    if feishu_user is not None:
                        ids.append("2"+str(request.id) + "2")
                        msgs.append(msg)
                    # log_info = f"用户{user.username} ({user.department.name}) 在 {get_date()} 拒绝 {request.initiator.username} 的转移请求 {asset.name}"
                    # log = Log(log=log_info, type = 1, entity=user.entity)
                    # log.save()

            else:
                err_msg += f'第{idx+1}条想要处理的资产 {asset_name} 申请不符合要求; '

        if len(err_msg) > 0:
            return request_failed(1, err_msg[:-1], status_code=403)
        if len(ids) > 0:
            tenant = get_tenant()
            create_feishu_task(ids, request.initiator.username, msgs,tenant, "审批完成", "REJECTED", request.request_time, request.review_time)
        # loop.create_task(create_feishu_task(ids, user.entity.name, msgs,tenant, "申领", "REJECTED"))
        return request_success()
    
    return BAD_METHOD

@CheckRequire
def feishu(req: HttpRequest):
    body = json.loads(req.body.decode("utf-8"))
    print(body)
    action_type = body.get("action_type", "")
    instance_id = body.get("instance_id", "")
    user_id = body.get("user_id", "")
    id = instance_id[1:-1]
    status = ""
    if action_type == 'APPROVE':
        status = "APPROVED"
    elif action_type == 'REJECT':
        status = "REJECTED"
    try:
        id = int(id)
        msg = ""
        action = "action"
        user_name = ""
        if instance_id[0] == '1':
            request = NormalRequests.objects.filter(id=id).first()
            if request is not None:
                asset = request.asset
            else:
                return request_failed(-2, "没有对应请求", 404)
            type = request.type
            actions = ["", "申领", "退库", "维修"]
            if status == "APPROVED":
                request.result=1
                if type == 1:
                    action = "申领"
                    asset.owner = request.initiator.username
                    asset.state = 'IN_USE'
                    asset.operation = 'IN_USE'
                elif type == 2:
                    action = "退库"
                    asset.state = 'IDLE'
                    user_feishu = UserFeishu.objects.filter(user_id=user_id).first()
                    if user_feishu is not None and user_feishu.user_id != "":
                        open_id = user_feishu.open_id
                    else:
                        open_id = get_open_id(user_id)
                    feishu_user = UserFeishu.objects.filter(open_id=open_id).first()
                    username = feishu_user.username
                    user = User.objects.filter(username=username).first()
                    asset.owner = user.username
                    asset.operation = 'IDLE'
                elif type == 3:
                    action = "维修"
                    asset.state = 'IN_MAINTAIN'
                    asset.operation = 'IN_MAINTAIN'
                entity = request.initiator.entity.name
            elif status == "REJECTED":
                request.result = 2
                action = actions[type]
            initiator = request.initiator
            msg = f"{initiator.username} {action} {request.asset.name}"
            request.review_time = get_timestamp()
            request.save()
            asset.change_time = get_timestamp()
            asset.change_value = 0
            asset.save()
        elif instance_id[0] == '2':
            request = TransferRequests.objects.filter(id=id).first()
            if request is not None:
                asset = request.asset
            else:
                return request_failed(-2, "没有对应请求", 404)
            action = "转移"
            request.review_time = get_timestamp()
            if status == "APPROVED":
                request.result=1
                asset.owner = request.participant.username
                asset.position = request.position
                asset.operation = 'MOVE'
            elif status == "REJECTED":
                action = '拒绝'
                request.result = 2
            request.save()
            asset.change_time = get_timestamp()
            asset.change_value = 0
            asset.save()
            initiator = request.initiator
            msg = f"{initiator.username} 转移 {request.asset.name} 到 {request.participant.department.name} {request.participant.username}"
        tenant = get_tenant()
        create_feishu_task([instance_id],'Alice',[msg],tenant, action, status,request.request_time, get_timestamp())
    except Exception as e:
        print(e)
        return request_failed(-1, str(e), 400)
    return request_success()