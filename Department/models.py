from django.db import models

# Create your models here.
from mptt.models import MPTTModel, TreeForeignKey


class Department(MPTTModel):
    ''' department of an employer'''
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=30)
    parent = TreeForeignKey('self', blank=True, null=True, on_delete=models.CASCADE)
    def root(cls):
        ''' return the root of the tree'''
        return cls.objects.first().get_root()


class Entity(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=128)