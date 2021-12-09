from django.urls import path

from . import views

urlpatterns = [
    path('category/', views.HostCategoryListAPIView.as_view()),
    path('list', views.HostModelViewSet.as_view({
        'get': 'list',
        'post': 'create'
    })),
]
