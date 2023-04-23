from django.db import models
from utils import utils_time
from utils.utils_request import return_field

# Create your models here.
from mptt.models import MPTTModel, TreeForeignKey
from User.models import User
from Asset.models import Asset


class NormalRequests(models.Model):
    '''
    普通请求
    type=1，申领; type=2，退库; type=3，维修
    '''
    id = models.BigAutoField(primary_key=True)
    initiator = models.ForeignKey(User, on_delete=models.CASCADE)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    type = models.IntegerField(default=0)
    result = models.IntegerField(default=0)
    request_time = models.FloatField(default=utils_time.get_timestamp)
    review_time = models.FloatField(default=utils_time.get_timestamp)

    def serialize(self):
        type_str = ""
        if self.type == 1:
            type_str = "申领"
        elif self.type == 2:
            type_str = "退库"
        elif self.type == 3:
            type_str = "维修"
        return {
            "id": self.id,
            "initiator": self.initiator.username,
            "asset": self.asset.name,
            "type_id": self.type,
            "type":type_str,
            "result": self.result,
            "request_time": self.request_time,
            "review_time": self.review_time
        }
    

class TransferRequests(models.Model):
    '''转移请求'''
    id = models.BigAutoField(primary_key=True)
    initiator = models.ForeignKey(User,verbose_name="initiator", related_name="initiator", on_delete=models.CASCADE)
    participant = models.ForeignKey(User,verbose_name="participant", related_name="participant", on_delete=models.CASCADE)
    position = models.CharField(max_length=100)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    type = models.IntegerField(default=0)
    result = models.IntegerField(default=0)
    request_time = models.FloatField(default=utils_time.get_timestamp)
    review_time = models.FloatField(default=utils_time.get_timestamp)

    def serialize(self):
        return {
            "id": self.id,
            "initiator": self.initiator,
            "participant": self.participant,
            "position": self.position,
            "asset": self.asset,
            "type": self.type,
            "result": self.result,
            "request_time": self.request_time,
            "review_time": self.review_time
        }
