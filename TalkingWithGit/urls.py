from django.urls import path

from . import views

urlpatterns = [
    path('repositories/add', views.GitTestCreateView.as_view(), name='git-test.new'),
    path('repositories', views.GitTestListView.as_view(), name='git-test.list'),
    path('repositories/<int:pk>/update', views.GitTestUpdateView.as_view(), name='git-test.update'),
    path('repositories/<int:pk>/detail', views.GitTestDetailView.as_view(), name='git-test.detail'),
    path('repositories/<int:pk>/delete', views.GitTestDeleteView.as_view(), name='git-test.delete'),
    path('repositories/<int:pk>/files/<str:branch>/<str:relative_dir>', views.RenderTreeView.as_view(), name='git-test.view_folder'),
    path('repositories/<int:pk>/history/<str:branch>', views.CommitHistoryView.as_view(), name='git-test.view_commit_history'),
]