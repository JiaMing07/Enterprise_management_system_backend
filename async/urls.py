from django.urls import path, include
from .views import *

urlpatterns = [
    path('test', test),
    path('list', show_list),
    path('add', add),
    path('failed', failed_list),
    path('restart', restart),
    path('test2', test2),
    path('model', model_list)
]