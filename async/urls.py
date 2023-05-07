from django.urls import path, include
from .views import *

urlpatterns = [
    path('test', test),
    path('list', show_list),
    path('add', add)
]