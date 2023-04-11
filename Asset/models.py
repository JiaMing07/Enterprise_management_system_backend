from django.db import models
from utils.utils_request import return_field

# Create your models here.
from mptt.models import MPTTModel, TreeForeignKey
from Department.models import Department, Entity

class AssetCategory(MPTTModel):
    '''资产类型'''
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50)
    parent = TreeForeignKey('self', blank=True, null=True, on_delete=models.CASCADE)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)


class Asset(MPTTModel):
    '''资产'''
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=300)
    position = models.CharField(max_length=300)
    value = models.BigIntegerField(default=0)
    owner = models.CharField(max_length=50)
    number = models.BigIntegerField(default=1)
    is_number = models.BooleanField(default=False)
    state = models.CharField(max_length=50, default='IDLE')
    category = models.ForeignKey(AssetCategory, on_delete=models.CASCADE)
    parent = TreeForeignKey('self', blank=True, null=True, on_delete=models.CASCADE)


class Attribute(models.Model):
    '''自定义属性'''
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)


class AssetAttribute(models.Model):
    id = models.BigAutoField(primary_key=True)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    description = models.CharField(max_length=300)