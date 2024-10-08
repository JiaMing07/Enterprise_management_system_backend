from django.db import models
from utils import utils_time
from utils.utils_request import return_field
from simple_history.models import HistoricalRecords

# Create your models here.
from mptt.models import MPTTModel, TreeForeignKey
from Department.models import Department, Entity

class AssetCategory(MPTTModel):
    '''资产类型'''
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50)
    parent = TreeForeignKey('self', blank=True, null=True, on_delete=models.CASCADE)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    is_number = models.BooleanField(default=True)
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
            "parentName": parent_name,
            "is_number": self.is_number,
        }
    
    def sub_tree(self):
        children_list = []
        children = self.get_children()
        for child in children:
            children_list.append(child.sub_tree())
        
        return {
            "categoryName": self.name,
            "is_number": self.is_number,
            "sub-categories": children_list,
        }
    
    class Meta:
        unique_together = ['entity', 'name']

class Asset(MPTTModel):
    '''资产'''
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=300)
    position = models.CharField(max_length=300)
    value = models.BigIntegerField(default=0)
    owner = models.CharField(max_length=50)
    number = models.BigIntegerField(default=1)
    state = models.CharField(max_length=50, default='IDLE')
    category = models.ForeignKey(AssetCategory, on_delete=models.CASCADE)
    parent = TreeForeignKey('self', blank=True, null=True, on_delete=models.CASCADE)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    created_time = models.FloatField(default=utils_time.get_timestamp)
    life = models.BigIntegerField(default=10) # 寿命
    image_url = models.CharField(max_length=300)
    # history method
    change_value = models.BigIntegerField(default=0)
    operation = models.CharField(max_length=50, default='add')
    change_time = models.FloatField(default=utils_time.get_timestamp)
    history = HistoricalRecords(excluded_fields=['lft', 'rght', 'tree_id', 'level', 'description', 'position', 'entity', 'created_time', 'image_url'])
    @classmethod
    def root(cls):
        ''' return the root of the tree'''
        return cls.objects.first().get_root()

    def serialize(self):
        if self.parent is None:
            parent_name = ''
        else:
            parent_name = self.parent.name
            if parent_name == self.entity.name:
                parent_name = ''
        return {
            "id": self.id,
            "assetName": self.name,
            "parentName": parent_name,
            "category": self.category.name,
            "description": self.description,
            "position": self.position,
            "value": self.value,
            "user": self.owner,
            "number": self.number,
            "state": self.state,
            "entity": self.entity.name,
            "department": self.department.name,
            "createTime": self.created_time,
            "life": self.life,
            "image": self.image_url,
        }
    
    def sub_tree(self):
        children_list = []
        children = self.get_children()
        for child in children:
            children_list.append(child.sub_tree())
        
        return {
            "assetName": self.name,
            "sub-assets": children_list,
        }
    class Meta:
        unique_together = ['entity', 'name']
        indexes = [models.Index(fields=['entity', 'department', 'name', 'id'])]

    def __str__(self):
        return self.name

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
    
    class Meta:
        unique_together = ['entity', 'name']

class AssetAttribute(models.Model):
    id = models.BigAutoField(primary_key=True)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    description = models.CharField(max_length=300)

    def serialize(self):
        return {
            "id": self.id,
            "asset": self.asset.name,
            "attribute": self.attribute.name,
            "description": self.description,
        }
    
class Label(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50)
    depart = models.ForeignKey(Department, on_delete=models.CASCADE)
    asset_name = models.BooleanField(default=True)
    entity = models.BooleanField(default=True)
    category = models.BooleanField(default=True)
    department = models.BooleanField(default=True)
    attribute = models.BooleanField(default=True)
    number = models.BooleanField(default=True)
    position = models.BooleanField(default=True)
    description = models.BooleanField(default=True)
    QRcode = models.BooleanField(default=True)
    value = models.BooleanField(default=True) 

class Warning(models.Model):
    id = models.BigAutoField(primary_key=True)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    ageLimit = models.BigIntegerField(default=0)
    numberLimit = models.BigIntegerField(default=0)

    def serialize(self):
        return {
            "asset": self.asset.name,
            "department": self.department.name,
            "ageLimit": self.ageLimit,
            "numberLimit": self.numberLimit,
        }