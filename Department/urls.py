from django.urls import path, include
import Department.views as views

urlpatterns = [
    path('startup', views.startup),
    path('entity/add', views.add_entity),
    # path('department/add', views.add_department),
]