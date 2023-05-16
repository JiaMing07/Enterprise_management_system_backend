import requests
import json
from User.models import *
from Department.models import *
from utils.utils_time import *

def get_asset_super(department, status, title, start_time, end_time):
    ancestor_list = department.get_ancestors(include_self=True)
    print(ancestor_list)
    asset_supers = User.objects.filter(asset_super=True).filter(department__in=ancestor_list)
    tasks = []
    num = 0
    for ass in asset_supers:
        user = UserFeishu.objects.filter(username=ass.username).first()
        if user is not None:
            if user.open_id == "" or user.open_id is None:
                user.open_id = get_feishu_id(user)
                user.save()
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
    print("finish")
    return tasks

def create_feishu_task(ids, initiator_name, msgs, tenant_access_code, title, status, start_time = get_timestamp(), end_time=0):
    url = "https://open.feishu.cn/open-apis/approval/v4/external_instances"
    initiator = User.objects.filter(username=initiator_name).first()
    if end_time != 0:
        end_time = str(end_time*1000).split('.')[0]
    tasks = get_asset_super(initiator.department,status,title,start_time,end_time)
    feishu_user = UserFeishu.objects.filter(username=initiator_name).first()
    if feishu_user is not None:
        if feishu_user.open_id == "" or feishu_user.open_id is None:
            feishu_user.open_id = get_feishu_id(feishu_user)
            feishu_user.save()
        for idx,id in enumerate(ids):
            payload = json.dumps({
                "approval_code": "531E32E9-3867-486C-A0DD-378CD5B08CB7",
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
                    "mobile_link": "http://applink.feishu.cn/sso/common?redirectUrl=/seeyon/main.do?method=main&client=pc",
                    "pc_link": "http://applink.feishu.cn/sso/common?redirectUrl=/seeyon/main.do?method=main&client=pc"
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
            print(response.text)
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
    return response.json()['data']['user_list'][0]['user_id']

def get_user_id(mobile_):
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
    return response.json()['data']['user_list'][0]['user_id']

def get_dep_son(department_id):
    depart_id = department_id
    url = "https://open.feishu.cn/open-apis/contact/v3/departments/:{depart_id}/children?fetch_child=true"
    tenant = get_tenant()
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {tenant}'
    }

    response = requests.request("GET", url, headers=headers)
    return response.json()['data']['items']

def get_one_dep(department_id):
    depart_id = department_id
    url = "https://open.feishu.cn/open-apis/contact/v3/departments/:{depart_id}"
    tenant = get_tenant()
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {tenant}'
    }

    response = requests.request("GET", url, headers=headers)
    return response.json()['data']['department']

def get_users(department_id):
    depart_id = department_id
    url = "https://open.feishu.cn/open-apis/contact/v3/users/find_by_department?department_id={depart_id}"
    tenant = get_tenant()
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {tenant}'
    }

    response = requests.request("GET", url, headers=headers)
    return response.json()['data']['items']