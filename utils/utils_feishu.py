import requests
import json
from User.models import *
from Department.models import *
from utils.utils_time import *

def get_asset_super(department, status, title):
    ancestor_list = department.get_ancestors(include_self=True)
    print(ancestor_list)
    asset_supers = User.objects.filter(asset_super=True).filter(department__in=ancestor_list)
    tasks = []
    num = 0
    for ass in asset_supers:
        user = UserFeishu.objects.filter(username=ass.username).first()
        if user is not None:
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
                    "create_time": "1638468921000",
                    "end_time": 0,
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
    tasks = get_asset_super(initiator.department,status,title)
    print("in2")
    print(UserFeishu.objects.all())
    print("in3")
    feishu_user = UserFeishu.objects.filter(username=initiator_name).first()
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
            "start_time": str(start_time*1000)[:-5],
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


    headers = {
    'Authorization': 'Bearer t-g1045ffoQJLKXKTIPO2MJ6NQEFWKB7VYTJPUMP2Q'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    body = response.json()
    return body['data']['user']['open_id']