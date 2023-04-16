from django.urls import path, include
import Asset.views as views

urlpatterns = [
    path('category/list', views.asset_category_list),
    path('category/add', views.asset_category_add),
    path('category/delete', views.asset_category_delete),
    path('list', views.asset_list),
    path('add', views.asset_add),
    path('delete', views.asset_delete),
    path('attribute/add', views.attribute_add),
    path('attribute/<department>/list', views.attribute_list),
    path('attribute/delete', views.attribute_delete),
    path('attribute', views.asset_attribute),
    path('<assetName>', views.asset_assetName),
]