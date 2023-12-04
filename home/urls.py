from django.urls import path

from . import views

urlpatterns = [
    path('home', views.HomeView.as_view()),
    path('authorised', views.AuthorisedView.as_view()),
    path('login', views.LoginInterfaceView.as_view()),
]