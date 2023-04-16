from django.urls import path, include
import Asset.views as views

urlpatterns = [
    path('category/list', views.asset_category_list),
    path('category/add', views.asset_category_add),
    path('list', views.asset_list),
    path('add', views.asset_add),
    path('attribute/add', views.attribute_add),
    path('attribute/<department>/list', views.attribute_list),
    path('attribute', views.asset_attribute),
    path('tree', views.asset_tree)
]