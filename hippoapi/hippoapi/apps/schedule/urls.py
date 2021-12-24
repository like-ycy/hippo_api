from django.urls import path

from . import views

urlpatterns = [
    path('periods/', views.PeriodView.as_view()),
    path('tasks/', views.TaskView.as_view()),
]
