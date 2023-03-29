from django.urls import path, include
import User.views as views

urlpatterns = [
    path('startup', views.startup),
    path('login/normal', views.login_normal),
    path('add', views.user_add),
    path('logout/normal', views.logout_normal),
    path('lock', views.user_lock),
    path('list', views.user_list),
]
