from django.db import models
from datetime import datetime, timedelta


from django.db import models

from eam_backend.settings import SECRET_KEY
from Department.models import Department, Entity
import jwt


class User(models.Model):
    '''
    User
    '''
    username = models.CharField(max_length=50, primary_key=True, unique=True, verbose_name='用户名')
    password = models.CharField(max_length = 50, default='123456')
    department = models.ForeignKey(Department, on_delete=models.SET(Department.root))
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    active = models.BooleanField(auto_created=True, default=True)
    token = models.CharField(max_length=200, auto_created=True, default='', blank=True)
    entity_super = models.BooleanField(default=False)
    system_super = models.BooleanField(default=False)
    asset_super = models.BooleanField(default=False)

    def check_password(self, pwd):
        if pwd == self.password:
            return True
        else:
            return False
    
    def generate_token(self):
        payload = {'exp': datetime.now() + timedelta(days=1), 'iat': datetime.utcnow(), 'username': self.username}
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        return token
    
    def serialize(self):
        authority = ""
        if self.system_super:
            authority+="system_super"
        if self.entity_super:
            if authority != "":
                authority += " "
            authority+="entity_super"
        if self.asset_super:
            if authority != "":
                authority += " "
            authority+="asset_super"
        if authority == "":
            authority = "staff"
        is_active = ""
        if self.active:
            is_active="未被锁定"
        else:
            is_active="锁定"
        return {
            "username": self.username,
            "entity": self.entity.name,
            "department": self.department.name,
            "active_str": is_active,
            "active": self.active,
            "authority": authority, 
            "token": self.token,
        }
# Create your models here.
