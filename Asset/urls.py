from django.urls import path, include
import Asset.views as views

urlpatterns = [
    path('attribute/add', views.attribute_add),
]