from django.urls import path, re_path

from . import views

urlpatterns = [
    path('app/', views.ReleaseAPIView.as_view()),
    path('new', views.NewReleaseAPIView.as_view()),
    path('apply', views.ReleaseApplyViewSet.as_view({'get': 'list', 'post': 'create', })),
    path('apply/status', views.ReleaseApplyStatusAPIView.as_view()),
    # 切换环境时获取当前环境下的所有发布应用
    path('envs/apps', views.EnvsAppsAPIView.as_view()),
    # 获取git 仓库的分支数据
    path('git/branch', views.GitBranchAPIView.as_view()),
    re_path('release_ap/(?P<pk>\d+)/', views.ReleaseApplyViewSet.as_view({'patch': 'partial_update', })),
]
