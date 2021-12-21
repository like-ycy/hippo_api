from django.urls import path

from . import views

urlpatterns = [
    path('environment/', views.EnvironmentAPIView.as_view({'post': 'create', 'get': 'list'})),
]
