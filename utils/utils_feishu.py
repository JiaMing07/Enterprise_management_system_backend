import requests
import json
from User.models import *
from Department.models import *
from Request.models import *
from utils.utils_time import *
from utils.utils_request import *

def get_asset_super(department, status, title, start_time, end_time):
    ancestor_list = department.get_ancestors(include_self=True)
    asset_supers = User.objects.filter(asset_super=True).filter(department__in=ancestor_list)
    tasks = []
    num = 0
    for ass in asset_supers:
        user = UserFeishu.objects.filter(username=ass.username).first()
        if user is not None:
            if user.open_id == "" or user.open_id is None:
                user.open_id = get_feishu_id(user)
                user.save()
            if user.open_id == "":
                continue
            task = {
                    "action_configs": [
                        {
                            "action_name": "@i18n@1",
                            "action_type": "APPROVE",
                            "is_need_attachment": False,
                            "is_need_reason": False,
                            "is_reason_required": False
                        },{
                            "action_name": "@i18n@1",
                            "action_type": "REJECT",
                            "is_need_attachment": False,
                            "is_need_reason": False,
                            "is_reason_required": False
                        }
                    ],
                    "action_context": "123456",
                    "create_time": str(start_time*1000).split('.')[0],
                    "end_time": end_time,
                    "extra": "",
                    "links": {
                        "mobile_link": "http://",
                        "pc_link": "http://"
                    },
                    "status": status,
                    "task_id": str(num+1),
                    "title": title,
                    "update_time": "1638468921000",
                    "open_id": f"{user.open_id}"
                }
            tasks.append(task)
            num += 1
    return tasks

def create_feishu_task(ids, initiator_name, msgs, tenant_access_code, title, status, start_time = get_timestamp(), end_time=0):
    url = "https://open.feishu.cn/open-apis/approval/v4/external_instances"
    initiator = User.objects.filter(username=initiator_name).first()
    if end_time != 0:
        end_time = str(end_time*1000).split('.')[0]
    if status != 'DELETED':
        tasks = get_asset_super(initiator.department,status,title,start_time,end_time)
    else:
        tasks = []
    feishu_user = UserFeishu.objects.filter(username=initiator_name).first()
    if feishu_user is not None:
        if feishu_user.open_id == "" or feishu_user.open_id is None:
            feishu_user.open_id = get_feishu_id(feishu_user)
            feishu_user.save()
        if feishu_user.open_id == "":
            return "not in entity"
        for idx,id in enumerate(ids):
            payload = json.dumps({
                "approval_code": "27159948-7DCF-4111-A66D-29C9C815CD7E",
                # "approval_code": "6506F1FB-8749-4173-BAD6-3FE0EC60BFAD",
                "end_time": end_time,
                "extra": "",
                "form": [
                    {
                        "name": "@i18n@2",
                        "value": f"{msgs[idx]}"
                    }
                ],
                "i18n_resources": [
                    {
                        "is_default": True,
                        "locale": "zh-CN",
                        "texts": [
                            {
                                "key": "@i18n@1",
                                "value": "用户审批"
                            },
                            {
                                "key": "@i18n@2",
                                "value": "申请"
                            },
                            {
                                "key": "@i18n@3",
                                "value": "2022-07-06"
                            }
                        ]
                    }
                ],
                "instance_id": str(id),
                "links": {
                    "mobile_link": "https://EAM-Frontend-BugHunters.app.secoder.net",
                    "pc_link": "https://EAM-Frontend-BugHunters.app.secoder.net"
                },
                "open_id": f"{feishu_user.open_id}",
                "start_time": str(start_time*1000).split('.')[0],
                "status": status,
                "task_list": tasks,
                "title": "@i18n@1",
                "update_mode": "REPLACE",
                "update_time": "1657093395000"
            })
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {tenant_access_code}'
            }
            response = requests.request("POST", url, headers=headers, data=payload)
    return "ok"

def get_tenant():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = json.dumps({
        "app_id": "cli_a4ebb92f303ad013",
        "app_secret": "Ejol3MvwF9B6Iai3Z9a1IdqRnyPnjeOd"
    })


    headers = {
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json()['tenant_access_token']

def get_open_id(user_id):
    url = f"https://open.feishu.cn/open-apis/contact/v3/users/{user_id}?department_id_type=open_department_id&user_id_type=user_id"
    payload = ''
    tenant = get_tenant()


    headers = {
    'Authorization': f'Bearer {tenant}'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    body = response.json()
    open_id = body['data']['user']['open_id']
    print(f"open_id={open_id}")
    return body['data']['user']['open_id']

def get_feishu_id(feishu_user):
    mobile = feishu_user.mobile
    tenant = get_tenant()
    url = "https://open.feishu.cn/open-apis/contact/v3/users/batch_get_id?user_id_type=open_id"
    payload = json.dumps({
        "mobiles": [
            mobile
        ]
    })


    headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {tenant}'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    try:
        open_id = response.json()['data']['user_list'][0]['user_id']
    except:
        open_id = ""
    return open_id

def get_user_id(mobile_):
    mobile = mobile_
    tenant = get_tenant()
    url = "https://open.feishu.cn/open-apis/contact/v3/users/batch_get_id?user_id_type=user_id"
    payload = json.dumps({
        "mobiles": [
            mobile
        ]
    })


    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {tenant}'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    try:
        user_id = response.json()['data']['user_list'][0]['user_id']
    except:
        user_id = ""
    return user_id

def get_open_id(mobile_):
    mobile = mobile_
    tenant = get_tenant()
    url = "https://open.feishu.cn/open-apis/contact/v3/users/batch_get_id?user_id_type=open_id"
    payload = json.dumps({
        "mobiles": [
            mobile
        ]
    })


    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {tenant}'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    try: 
        open_id = response.json()['data']['user_list'][0]['user_id']
    except:
        open_id = ""
    return open_id

def get_dep_son(department_id):
    depart_id = department_id
    url = f"https://open.feishu.cn/open-apis/contact/v3/departments/{depart_id}/children?fetch_child=true"
    tenant = get_tenant()
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {tenant}'
    }

    response = requests.request("GET", url, headers=headers)
    return response.json()['data']['items']

def get_one_dep(department_id):
    depart_id = department_id
    url = f"https://open.feishu.cn/open-apis/contact/v3/departments/{depart_id}"
    tenant = get_tenant()
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {tenant}'
    }

    response = requests.request("GET", url, headers=headers)
    return response.json()['data']['department']

def get_parent(department_id):
    url = f"https://open.feishu.cn/open-apis/contact/v3/departments/parent?department_id={department_id}"
    tenant = get_tenant()
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {tenant}'
    }

    response = requests.request("GET", url, headers=headers)
    if "items" in response.json()['data']:
        print("有的啦!")
        return response.json()['data']['items'][0]
    
    return None

def get_users(department_id):
    depart_id = department_id
    url = f"https://open.feishu.cn/open-apis/contact/v3/users/find_by_department?department_id={depart_id}"
    tenant = get_tenant()
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {tenant}'
    }

    response = requests.request("GET", url, headers=headers)
    # print(f"msg = {response.json()['msg']}")
    # print(f"has_more = {response.json()['data']['has_more']}")

    if "items" in response.json()['data']:
        print("有的啦!")
        return response.json()['data']['items']
    
    return None

def feishu_callback(id, instance_id, status, user_id):
    try:
        id = int(id)
        msg = ""
        action = "action"
        user_name = ""
        code = 0
        msg = "ok"
        status_code = 200
        if instance_id[0] == '1':
            request = NormalRequests.objects.filter(id=id).first()
            if request is not None:
                asset = request.asset
            else:
                code = -2
                msg = "没有对应请求"
                status_code = 404
                return code, msg, status_code
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
                code = -2
                msg = "没有对应请求"
                status_code = 404
                return code, msg, status_code
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
        create_feishu_task([instance_id], initiator.username,[msg],tenant, action, status,request.request_time, get_timestamp())
    except Exception as e:
        print(e)
        code = -1
        msg = str(e)
        status_code = 400
        return code, msg, status_code