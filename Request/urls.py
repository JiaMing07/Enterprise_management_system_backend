from django.urls import path, include
import Request.views as views

urlpatterns = [
    path('waiting', views.waiting_list),
    path('return', views.requests_return),
]