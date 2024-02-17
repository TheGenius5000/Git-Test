from django.urls import path, include

from . import views

urlpatterns = [
    path('writer', views.WriterListView.as_view(), name="writer.list"),
    path('writer/<int:pk>', views.WriterDetailView.as_view(), name="writer.detail"),
    path('writer/<int:pk>/edit', views.WriterUpdateView.as_view(), name="writer.update"),
    path('writer/<int:pk>/delete', views.WriterDeleteView.as_view(), name="writer.delete"),
    path('writer/new', views.WriterCreateView.as_view(), name="writer.new"),
]
