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
    path('repositories/<int:repo_pk>/merges/new', views.GitTestMergeRequestCreateView.as_view(), name='git-test.merge_request_create'),
    path('repositories/<int:repo_pk>/merges/<int:pk>', views.GitTestMergeRequestDetailView.as_view(), name='git-test.merge_request_detail'),
    path('repositories/<int:repo_pk>/merges/<int:pk>/delete', views.GitTestMergeRequestDeleteView.as_view(), name='git-test.merge_request_delete'),
    path('repositories/<int:pk>/merges/history', views.GitTestMergeRequestHistoryView.as_view(), name='git-test.merge_request_history'),
    path('repositories/<int:pk>/files/<str:branch>/<str:relative_dir>/<str:filename>', views.EditFileView.as_view(), name='git-test.edit_file'),
    path('repositories/<int:pk>/<str:branch>/compare/<str:commit1hash>', views.SelectCommitCompareView.as_view(), name='git-test.compare_select_commit2'),
    path('repositories/<int:pk>/<str:branch>/compare/<str:commit1hash>/<str:commit2hash>', views.CompareCommitSameBranchView.as_view(), name='git-test.compare_commit_same_branch'),
    path('repositories/<int:pk>/merge_conflict', views.ResolveMergeConflictView.as_view(), name='git-test.resolve_merge_conflict'),
    path('repositories/<int:pk>/compare/<str:branch1>/<str:branch2>', views.CompareBranchesView.as_view(), name='git-test.compare_branches'),
]