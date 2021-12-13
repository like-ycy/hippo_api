from django.urls import path

from . import views

urlpatterns = [
    path('app', views.ReleaseAPIView.as_view()),
    path('new', views.NewReleaseAPIView.as_view()),
]
