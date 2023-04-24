from django.urls import path, include
import Request.views as views

urlpatterns = [
    path('waiting', views.waiting_list),
    path('return', views.requests_return),
    path('repair', views.requests_repair),
    path('transfer', views.request_transfer),
    path('require', views.requests_require)
]