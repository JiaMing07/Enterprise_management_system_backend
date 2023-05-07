import uuid
from celery.signals import before_task_publish
from celery import states
from django.db import transaction
from .models import AsyncTask
from django_celery_results.models import TaskResult
from django.db.models.signals import post_save
from django.dispatch import receiver
from User.models import User, Menu
from Department.models import Department, Entity
from Asset.models import Attribute, Asset, AssetAttribute, AssetCategory, Label
from eam_backend.celery import app
from utils.utils_getbody import get_args
import time


@app.task(name='add_assets', bind=True)
def add_assets(assets_new, username):
    user = User.objects.filter(username=username).first()
    entity=user.entity
    err_msg=""
    for idx, asset_single in enumerate(assets_new):
        name, parentName, description, position, value, department, number, categoryName, image_url = get_args(
        asset_single, ["name", "parent", "description", "position", "value", "department", "number", "category", "image"], 
        ["string", "string", "string", "string", "int", "string", "int", "string", "string"])
        state = asset_single.get('state', 'IDLE')
        owner = asset_single.get('owner', "")
        def check_length(string, lowerbound, upperbound, name,err_msg):
            if lowerbound < len(string) <=upperbound:
                err_msg += f"Bad length of [{name}]；"
        check_length(name, 0, 50, "assetName")
        check_length(parentName, -1, 50, "parentName")
        check_length(department, -1, 30, "department")
        check_length(categoryName, 0, 50, "categoryName")
        check_length(description, 0, 300, "description")
        check_length(position, 0, 300, "position")
        check_length(image_url, -1, 300, "imageURL")
        if parentName == "":
            parentName = entity.name
            parent = Asset.objects.filter(name=entity.name).first()
            if parent is None:
                parent = Asset(name=entity.name, owner=user.username, 
                            category=AssetCategory.root(), entity=entity, department=Department.objects.filter(entity=entity, name=entity.name).first(), parent=Asset.root())
                parent.save()
            if department == "":
                department = user.department
            else:
                department = Department.objects.filter(entity=entity, name=department).first()
                if department is None:
                    err_msg = err_msg +'第' +str(idx + 1) +"条资产录入失败，挂账部门不存在" + '；'
        else:
            parent = Asset.objects.filter(entity=entity, name=parentName).first()
            if parent is None:
                err_msg = err_msg +'第' +str(idx + 1) +"条资产录入失败，父资产不存在" + '；'
                continue
            if department == "":
                department = parent.department
            else:
                department = Department.objects.filter(entity=entity, name=department).first()
                if department is None:
                    err_msg = err_msg +'第' +str(idx + 1) +"条资产录入失败，挂账部门不存在" + '；'
                    continue
        category = AssetCategory.objects.filter(name=categoryName, entity=entity).first()
        if category is None:
            err_msg = err_msg +'第' +str(idx + 1) +"条资产录入失败，资产类型不存在" + '；'
            continue
        asset = Asset.objects.filter(entity=entity, name=name).first()
        if asset:
            err_msg = err_msg +'第' +str(idx + 1) +"条资产录入失败，该资产已存在" + '；'
            continue
        if owner == "":
            owner = User.objects.filter(entity=entity, department=department, asset_super=True).first()
            if owner is None:
                err_msg = err_msg +'第' +str(idx + 1) +"条资产录入失败，部门不存在资产管理员" + '；'
                continue
        else:
            owner = User.objects.filter(entity=entity, department=department, username=owner).first()
            if owner is None:
                err_msg = err_msg +'第' +str(idx + 1) +"条资产录入失败，挂账人不存在" + '；'
                continue
        ancestor_list = department.get_ancestors(include_self=True)
        if user.department not in ancestor_list:
            err_msg = err_msg +'第' +str(idx + 1) +"条资产录入失败，部门不在管理范围内" + '；'
            continue
        asset = Asset(name=name, description=description, position=position, value=value, owner=owner.username, number=number,
                    category=category, entity=entity, department=department, parent=parent, image_url=image_url,state=state)
        asset.save()

@app.task(name='test', bind=True)
def test1(self, body, username):
    print("in")
    print(username, self.request.id)
    AsyncTask.objects.create(task_id=self.request.id, initiator=username, body=body)
    time.sleep(5)
    print(f"created username {username}")
    return f"created username {username}"