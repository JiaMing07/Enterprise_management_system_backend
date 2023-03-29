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

    def serialize(self):
        return {
            "username": self.username, 
            "entity": self.entity.name,
            "department": self.department.name,
            "active" : self.active
        }
    
    def __str__(self) -> str:
        return f"User {self.username} of {self.entity.name}'s department {self.department.name}"

    def check_password(self, pwd):
        if pwd == self.password:
            print("True")
            return True
        else:
            print("False")
            print(pwd)
            print(self.password)
            return False
    
    def generate_token(self):
        payload = {'exp': datetime.now() + timedelta(days=1), 'iat': datetime.utcnow(), 'username': self.username}
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        return token
    
    def check_authen(self):
        if self.system_super == True:
            return "system_super"
        elif self.entity_super == True:
            return "entity_super"
        elif self.asset_super == True:
            return "asset_super"
        else:
            return "staff"
    
    def set_authen(self, authority):
        is_system_super = False
        is_entity_super = False
        is_asset_super = False
        if authority == "system_super":
            is_system_super = True
        elif authority == "entity_super":
            is_entity_super = True
        elif authority == "asset_super":
            is_asset_super = True
        return is_system_super, is_entity_super, is_asset_super
# Create your models here.
