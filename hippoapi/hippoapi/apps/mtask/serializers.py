from rest_framework import serializers

from .models import CmdTemplateCategory, CmdTemplate


class CmdTemplateModelSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = CmdTemplate
        fields = ["id", "name", "cmd", "description", "category_name", "category"]


class CmdTemplateCategoryModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CmdTemplateCategory
        fields = "__all__"
