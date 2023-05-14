from django.urls import path, include
import User.views as views

urlpatterns = [
    path('startup', views.startup),
    path('login/normal', views.login_normal),
    path('add', views.user_add),
    path('logout/normal', views.logout_normal),
    path('lock', views.user_lock),
    path('list', views.user_list),
    path('edit', views.user_edit),
    path('menu', views.user_menu),
    path('<userName>', views.user_userName),
    path('department/list', views.department_user_list),
    path('menu/list', views.menu_list),
    path('feishu/bind', views.feishu_bind),
    path('feishu/login', views.feishu_login),
    path('feishu/sync', views.feishu_sync)
]
