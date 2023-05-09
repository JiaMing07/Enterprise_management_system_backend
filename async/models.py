from django.db import models
from django.db import models
from django.db.models.functions import Now
from django_celery_results.models import TaskResult
from Department.models import *
# Create your models here.

class AsyncTask(models.Model):
    id = models.BigAutoField(primary_key=True)
    task = models.OneToOneField(TaskResult, to_field='task_id', on_delete=models.CASCADE)
    initiator = models.CharField(max_length=50)
    body = models.TextField()

    def serialze(self):
        return {
            'task_id': self.task.task_id,
            'status': self.task.status,
            'start_time': self.task.date_created,
            'end_time':self.task.date_done,
            'initiator': self.initiator,
            'result':self.task.result[2:-2],
            'body': self.body
        }
    
class AsyncModel(models.Model):
    id = models.BigAutoField(primary_key=True)
    initiator = models.CharField(max_length=50)
    body = models.JSONField()
    start_time = models.CharField(max_length=50)
    end_time = models.CharField(max_length=50)
    result = models.TextField()
    status = models.CharField(max_length=20)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)

    def serialize(self):
        return {
            'id': self.id,
            'status': self.status,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'initiator': self.initiator,
            'result': self.result
        }