import requests
import json
from User.models import *
from Department.models import *

async def get_asset_super(entity, status, title):
    asset_supers = User.objects.filter(entity=entity, asset_super=True)
    tasks = []
    num = 0
    for ass in asset_supers:
        user = UserFeishu.objects.filter(username=ass.name).afirst()
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
                    "open_id": user.open_id
                }
            tasks.append(task)
            num += 1
    return tasks

def create_feishu_task(ids, initiator, msg, tenant_access_code, title, status):
    url = "https://open.feishu.cn/open-apis/approval/v4/external_instances"
    tasks = get_asset_super(initiator.entity,status,title)
    for id in ids:
        payload = json.dumps({
            "approval_code": "EC2FD08D-B00C-4D69-965E-F5BA2B181AC5",
            "end_time": 0,
            "extra": "",
            "form": [
                {
                    "name": "@i18n@2",
                    "value": f"{msg}"
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
            "open_id": "ou_8c87029791feec2705633229bf596648",
            "start_time": "1657093395000",
            "status": status,
            "task_list": [
                {
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
                    "task_id": str(id+1),
                    "title": title,
                    "update_time": "1638468921000",
                    "open_id": "ou_8c87029791feec2705633229bf596648"
                }
            ],
            "title": "@i18n@1",
            "update_mode": "REPLACE",
            "update_time": "1657093395000"
        })
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {tenant_access_code}'
        }
    return "ok"

