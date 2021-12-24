from django.urls import path

from . import views

urlpatterns = [
    path('cpu/', views.MonitorViewSet.as_view({"get": "cpu"})),
]
