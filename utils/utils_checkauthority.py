from User.models import User, Menu
from django.http import HttpRequest
from eam_backend.settings import SECRET_KEY
from utils.utils_request import request_failed
from utils.utils_require import CheckRequire
import datetime
import jwt


def CheckToken(req: HttpRequest):
    try:
        token = req.COOKIES['token']
    except KeyError:
        raise KeyError("Token未给出")
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        decode = jwt.decode(token, SECRET_KEY, leeway=datetime.timedelta(days=3650), algorithms=['HS256'])
        user = User.objects.filter(username=decode['username']).first()
        user.token = ''
        user.save()
        raise jwt.ExpiredSignatureError("Token已过期")
    except jwt.InvalidTokenError:
        raise jwt.InvalidTokenError("Token不合法")
    return token, decoded

def CompareAuthority(req: HttpRequest, authority):
    token, decoded = CheckToken(req)
    user = User.objects.filter(username=decoded['username']).first()
    if user is None:
        return "不存在对应的用户"
    if user.token != token:
        return "用户已在其他地方登录，请退出后重新登陆"
    have_authority = False
    for au in authority:
        if user.check_authen() == au:
            have_authority = True
    if have_authority == False:        
        return "没有操作权限"
    return "ok"
   
def CheckAuthority(req: HttpRequest, authority: list):
    msg = CompareAuthority(req, authority)
    assert msg == "ok", f"{msg}"

