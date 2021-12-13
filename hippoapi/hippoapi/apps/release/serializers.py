from rest_framework import serializers

from .models import ReleaseApp


class ReleaseAppModelSerializer(serializers.ModelSerializer):
    """应用发布序列化器"""

    class Meta:
        model = ReleaseApp
        fields = ["id", "name", "tag", "description"]
