from django.db import models
from utils.utils_request import return_field

# Create your models here.
from mptt.models import MPTTModel, TreeForeignKey
from utils.utils_request import return_field

class Entity(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=128)

    def serialize(self):
        departments = Department.objects.filter(entity=self)
        return {
            "id": self.id, 
            "name": self.name, 
            "departments": [ return_field(department.serialize(), ["id", "departmentName", "entityName", "parentName"])
                       for department in departments ]
        }
    
    def __str__(self) -> str:
        return self.name

    def serialize(self):
        departments = Department.objects.filter(entity=self)
        departments = departments.exclude(name=self.name)
        return {
            "id": self.id, 
            "name": self.name, 
            "departments": [ return_field(department.serialize(), ["id", "departmentName", "entityName", "parentName"])
                       for department in departments ]
        }
    
    def __str__(self) -> str:
        return self.name
    
    class Meta:
        db_table = "entity"

class Department(MPTTModel):
    ''' department of an employer'''
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=30)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    parent = TreeForeignKey('self', blank=True, null=True, on_delete=models.CASCADE)
    @classmethod
    def root(cls):
        ''' return the root of the tree'''
        return cls.objects.first().get_root()
    
    def serialize(self):
        entity_name = self.entity.name
        if self.parent is None:
            parent_name = 'None'
        else:
            parent_name = self.parent.name
        return {
            "id": self.id,
            "departmentName": self.name,
            "entityName": entity_name,
            "parentName": parent_name
        }
    
    def __str__(self) -> str:
        return f"{self.entity.name}'s department {self.name}"


