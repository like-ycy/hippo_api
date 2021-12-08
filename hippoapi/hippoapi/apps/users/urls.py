from django.urls import path
from rest_framework_jwt.views import refresh_jwt_token

from . import views

urlpatterns = [
    path("login/", views.LoginAPIView.as_view(), name="login"),
    # path('verify/', verify_jwt_token),  # 这是只是校验token有效性
    path(r'refresh/', refresh_jwt_token),  # 校验并生成新的token
]
