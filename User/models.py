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
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    active = models.BooleanField(auto_created=True, default=True)
    token = models.CharField(max_length=200, auto_created=True, default='', blank=True)
    entity_super = models.BooleanField(default=False)
    system_super = models.BooleanField(default=False)
    asset_super = models.BooleanField(default=False)


    def __str__(self) -> str:
        return f"User {self.username} of {self.entity.name}'s department {self.department.name}"

    def check_password(self, pwd):
        if pwd == self.password:
            return True
        else:
            return False
    
    def generate_token(self):
        payload = {'exp': datetime.utcnow() + timedelta(days=1), 'iat': datetime.utcnow(), 'username': self.username}
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
    
class Menu(models.Model):
    '''
    menu
    '''
    id = models.BigAutoField(primary_key=True)
    first = models.CharField(max_length=50)
    second = models.CharField(max_length=50)
    url = models.CharField(max_length=500,default='')
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    entity_show = models.BooleanField(default=False)
    asset_show = models.BooleanField(default=False)
    staff_show = models.BooleanField(default=False)

    def check_authen(self):
        au = ""
        if self.staff_show == True:
            au += "staff "
        if self.entity_show == True:
            au += "entity_super"
        if self.asset_show == True:
            au+= "asset_super"
        return au
    
    def __str__(self) -> str:
        return f'{self.first}_{self.second}_{self.check_authen()}'
    
    def set_authority(self, au: list):
        entity_show=False
        asset_show=False
        staff_show=False
        for authority in au:
            if authority == 'entity_super':
                entity_show = True
            if authority == 'asset_super':
                asset_show = True
            if authority == 'staff':
                staff_show = True
        return entity_show, asset_show, staff_show
    
    def serialize(self):
        return {
            "first": self.first,
            "second": self.second,
            "url": self.url
        }
    
    class Meta:
        unique_together = ['first', 'second', 'entity']
# Create your models here.

