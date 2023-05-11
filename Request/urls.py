from django.urls import path, include
import Request.views as views

urlpatterns = [
    path('waiting', views.waiting_list),
    path('return', views.requests_return),
    path('repair', views.requests_repair),
    path('transfer', views.request_transfer),
    path('require', views.requests_require),
    path('user', views.requests_user),
    path('list', views.requests_list),
    path('approve', views.requests_approve),
    path('disapprove', views.requests_disapprove),
    path('delete', views.requests_delete),
    path('number', views.requests_number),
]