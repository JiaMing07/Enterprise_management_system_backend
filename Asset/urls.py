from django.urls import path, include
import Asset.views as views

urlpatterns = [
    path('category/list', views.asset_category_list),
    path('category/add', views.asset_category_add),
    path('list', views.asset_list),
    path('add', views.asset_add),
]