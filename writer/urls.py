from django.urls import path, include

from . import views

urlpatterns = [
    path('writer', views.list),
    path('writer/<int:pk>', views.detail)
]