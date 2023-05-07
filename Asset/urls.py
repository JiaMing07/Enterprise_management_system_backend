from django.urls import path, include
import Asset.views as views

urlpatterns = [
    path('category/list', views.asset_category_list),
    path('category/add', views.asset_category_add),
    path('category/edit', views.asset_category_edit),
    path('category/delete', views.asset_category_delete),
    path('list', views.asset_list),
    path('tree', views.asset_tree),
    path('add', views.asset_add),
    path('edit', views.asset_edit),
    path('label', views.asset_label),   # place it to here and it can be right
    path('user', views.user_query),
    path('delete', views.asset_delete),
    path('idle', views.asset_idle),
    path('allocate', views.asset_allocate),
    path('add/list', views.asset_add_list),
    path('query/<type>/<description>/<attribute>', views.asset_query),
    path('retire', views.asset_retire),
    path('attribute/add', views.attribute_add),
    path('attribute/<department>/list', views.attribute_list),
    path('attribute/edit', views.attribute_edit),
    path('attribute/delete', views.attribute_delete),
    path('attribute', views.asset_attribute),
    path('category/<category_name>/number', views.asset_category_number),
    path('attribute/<assetName>', views.asset_attribute_list),
    path('assetSuper', views.asset_assetSuper),
    path('warning', views.asset_warning),
    path('warning/message', views.asset_warning_message),
    path('warning/<assetName>', views.asset_warning_assetName),
    path('<assetName>', views.asset_assetName),
]