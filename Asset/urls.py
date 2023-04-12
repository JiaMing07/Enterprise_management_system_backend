from django.urls import path, include
import Asset.views as views

urlpatterns = [
    path('attribute/add', views.attribute_add),
    path('attribute/<department>/list', views.attribute_list),
]