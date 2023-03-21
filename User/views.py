import json
from django.http import HttpRequest, HttpResponse

from User.models import User
from Department.models import Department, Entity
from utils.utils_request import BAD_METHOD, request_failed, request_success, return_field
from utils.utils_require import MAX_CHAR_LENGTH, CheckRequire, require
from utils.utils_time import get_timestamp

def check_for_user_data(body):
    # TODO Start: [Student] add checks for type of boardName and userName
    password = ""
    user_name = ""
    password = require(body, "password", "string", err_msg="Missing or error type of [password]")
    user_name = require(body, "username", "string", err_msg="Missing or error type of [userName]")
    # TODO End: [Student] add checks for type of boardName and userName
    
    assert 0 < len(user_name) <= 50, "Bad length of [username]"
    
    # TODO Start: [Student] add checks for length of userName and board
    assert 0 < len(password) <=50, "Bad length of [password]"
    # TODO End: [Student] add checks for length of userName and board
    
    
    return user_name, password

# Create your views here.
def startup(req: HttpRequest):
    return HttpResponse("Congratulations! You have successfully installed the requirements. Go ahead!")

def login_normal(req: HttpRequest):
    if req.method == "POST":
        body = json.loads(req.body.decode("utf-8"))
        user_name, password = check_for_user_data(body)
        user = User.objects.filter(username=user_name).first()
        if not user:
            return request_failed(2, "不存在该用户", status_code=404)
        else:
            if user.check_password(password):
                return request_success()
            else:
                return request_failed(2, "密码不正确", status_code=401)
    else:
        return BAD_METHOD