from django.urls import path, include
from .views import *

urlpatterns = [
    path('list', model_list),
    path('add', add),
    path('failed', failed_list),
    path('restart', restart),
]