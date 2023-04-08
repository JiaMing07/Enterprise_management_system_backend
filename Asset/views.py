from django.shortcuts import render
import json
from django.http import HttpRequest, HttpResponse

from utils.utils_request import BAD_METHOD, request_failed, request_success, return_field
from utils.utils_require import MAX_CHAR_LENGTH, CheckRequire, require
from utils.utils_time import get_timestamp
from utils.utils_getbody import get_args
from utils.utils_checklength import checklength
from utils.utils_checkauthority import CheckAuthority, CheckToken

from Asset.models import Attribute, Asset, AssetAttribute, AssetCategory

# Create your views here.

@CheckRequire    
def attribute_add(req: HttpRequest):
    if req.method == 'POST':
        name = json.loads(req.body.decode("utf-8")).get('name')

        # check format
        checklength(name, 0, 50, "atrribute_name")

        # filter whether exist
        attri = Attribute.objects.filter(name=name).first()
        if attri is not None:
            return request_failed(1, "自定义属性已存在", status_code=403)

        # save
        else:
            new_attri = Attribute(name=name)
            new_attri.save()
            return request_success()
   
    else:
        return BAD_METHOD