from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from .models import HostCategory, Host
from .serializers import HostCategoryModelSeiralizer, HostModelSerializers


class HostCategoryListAPIView(ListAPIView, CreateAPIView):
    queryset = HostCategory.objects.filter(is_show=True, is_delete=False).order_by("orders", "-id").all()
    serializer_class = HostCategoryModelSeiralizer
    permission_classes = [IsAuthenticated]


class HostModelViewSet(ModelViewSet):
    queryset = Host.objects.all()
    serializer_class = HostModelSerializers
    permission_classes = [IsAuthenticated]
