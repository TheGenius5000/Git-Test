from django.urls import path, include

from . import views

urlpatterns = [
    path('writer', views.WriterListView.as_view()),
    path('writer/<int:pk>', views.WriterDetailView.as_view())
]