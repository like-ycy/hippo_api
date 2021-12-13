from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from .models import Environment
from .serializers import EnvironmentModelSerializer


class EnvironmentAPIView(ModelViewSet):
    """代码发布环境视图，提供增删改查"""
    queryset = Environment.objects.all()
    serializer_class = EnvironmentModelSerializer
    permission_classes = [IsAuthenticated]
