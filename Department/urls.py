from django.urls import path, include
import Department.views as views

urlpatterns = [
    # path('startup', views.startup),
    path('entity/add', views.add_entity),
    path('department/add', views.add_department),
    path('entity/list', views.entity_list),
    path('entity/<entityName>/department/list', views.entity_entityName_department_list),
    path('entity/<entity_name>/list', views.entity_entity_name_list),
    path('entity/<entityName>/entitySuper', views.entity_entityName_entitySuper),
    path('department/delete', views.department_delete),
    path('entity/<entity_name>/delete', views.entity_delete),
    path('entity/department/subtree', views.entity_department_subtree),
    path('log', views.entity_log)
]