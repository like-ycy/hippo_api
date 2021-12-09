from rest_framework import serializers

from .models import HostCategory, Host


class HostCategoryModelSeiralizer(serializers.ModelSerializer):
    """主机分类的序列化器"""

    class Meta:
        model = HostCategory
        fields = ['id', 'name']


class HostModelSerializers(serializers.ModelSerializer):
    """主机信息的序列化器"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    password = serializers.CharField(max_length=32, write_only=True, label="登录密码")

    class Meta:
        model = Host
        fields = ['id', 'category', 'category_name', 'name', 'ip_addr', 'port', 'description', 'username', 'password']

    def validate(self, attrs):
        """当用户添加、编辑主机信息会自动执行这个方法"""
        ip_addr = attrs.get('ip_addr')
        port = attrs.get('port')
        username = attrs.get('username')
        password = attrs.get('password')
        # todo 验证主机信息是否正确
        return attrs

    def create(self, validated_data):
        """添加host记录，如果第一次添加host记录，那么需要我们生成全局的公钥和私钥"""
        ip_addr = validated_data.get('ip_addr')
        port = validated_data.get('port')
        username = validated_data.get('username')
        password = validated_data.get('password')

        # todo 生成公私钥和管理主机的公私钥

        # 剔除密码字段，保存host记录
        password = validated_data.pop('password')
        instance = Host.objects.create(
            **validated_data
        )
        return instance
