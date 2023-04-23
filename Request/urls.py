from django.urls import path, include
import Request.views as views

urlpatterns = [
    path('return', views.requests_return),
    path('waiting', views.waiting_list),
]