from django.urls import path

from . import views

urlpatterns = [
    path('environments/', views.EnvironmentAPIView.as_view({'post': 'create', 'get': 'list'})),
]
