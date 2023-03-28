from django.db import models

# Create your models here.
from mptt.models import MPTTModel, TreeForeignKey

class Entity(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=128, unique=True)

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


