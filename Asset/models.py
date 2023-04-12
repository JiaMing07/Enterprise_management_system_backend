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
    @classmethod
    def root(cls):
        ''' return the root of the tree'''
        return cls.objects.first().get_root()

    def serialize(self):
        entity_name = self.entity.name
        if self.parent is None:
            parent_name = ''
        else:
            parent_name = self.parent.name
        return {
            "id": self.id,
            "categoryName": self.name,
            "entityName": entity_name,
            "parentName": parent_name
        }


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
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    @classmethod
    def root(cls):
        ''' return the root of the tree'''
        return cls.objects.first().get_root()

    def serialize(self):
        if self.parent is None:
            parent_name = ''
        else:
            parent_name = self.parent.name
        return {
            "id": self.id,
            "assetName": self.name,
            "parentName": parent_name,
            "categoryName": self.category.name,
            "description": self.description,
            "position": self.position,
            "value": self.value,
            "owner": self.owner,
            "is_number": self.is_number,
            "number": self.number,
            "state": self.state,
            "entity": self.entity.name,
        }


class Attribute(models.Model):
    '''自定义属性'''
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "entity": self.entity.name,
            "department": self.department.name,
        }

class AssetAttribute(models.Model):
    id = models.BigAutoField(primary_key=True)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    description = models.CharField(max_length=300)