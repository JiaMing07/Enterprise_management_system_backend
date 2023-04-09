from django.urls import path, include
import Asset.views as views

urlpatterns = [
    path('category/list', views.asset_category_list),
    path('category/add', views.asset_category_add),
]