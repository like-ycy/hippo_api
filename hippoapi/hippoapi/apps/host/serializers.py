from django.conf import settings
from rest_framework import serializers

from utils.check_ssh import valid_ssh
from utils.key import AppSetting
from utils.ssh import SSH
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
        hostname = attrs.get('ip_addr')
        port = attrs.get('port')
        username = attrs.get('username')
        password = attrs.get('password')
        # 验证主机信息是否正确
        ret = valid_ssh(hostname, port, username, password)
        if not ret:
            raise serializers.ValidationError('主机ping失败')
        return attrs

    def create(self, validated_data):
        """添加host记录，如果第一次添加host记录，那么需要我们生成全局的公钥和私钥"""
        hostname = validated_data.get('ip_addr')
        port = validated_data.get('port')
        username = validated_data.get('username')
        password = validated_data.get('password')

        # 生成公私钥和管理主机的公私钥
        # 创建公私钥之前，我们先看看之前是否已经创建过公私钥了
        _cli = SSH(hostname, username, port, password)
        try:
            # 尝试从数据库中提取公私钥
            private_key, public_key = AppSetting.get(settings.DEFAULT_KEY_NAME)
        except KeyError as e:
            # 没有公私钥存储到数据库中，则生成公私钥
            private_key, public_key = _cli.generate_key()
            # 将公钥和私钥保存到数据库中
            AppSetting.set(settings.DEFAULT_KEY_NAME, private_key, public_key, 'ssh全局秘钥对')

        # 上传公钥到远程主机
        try:
            _cli.add_public_key(public_key)
        except Exception as e:
            raise serializers.ValidationError('添加远程主机公钥失败，请检查输入的主机信息!')

        # 剔除密码字段，保存host记录
        validated_data.pop('password')
        instance = Host.objects.create(
            **validated_data
        )
        return instance
