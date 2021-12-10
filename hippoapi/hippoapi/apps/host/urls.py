from django.urls import path, re_path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("host", views.HostModelViewSet, basename="host"),

urlpatterns = [
                  path('category/', views.HostCategoryListAPIView.as_view()),
                  path('host_excel/', views.HostExcelView.as_view()),
                  re_path('^file/(?P<pk>\d+)/$', views.HostFileView.as_view(
                      {'get': 'get_folders', 'post': 'upload_file', 'delete': 'delete_file'})),
                  re_path('^download/(?P<pk>\d+)/$', views.HostFileView.as_view({'get': 'get_file'})),

              ] + router.urls
