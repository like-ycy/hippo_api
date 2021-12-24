from rest_framework import serializers

from .models import ReleaseApp, ReleaseApply


class ReleaseAppModelSerializer(serializers.ModelSerializer):
    """应用发布序列化器"""

    class Meta:
        model = ReleaseApp
        fields = ["id", "name", "tag", "description", "user"]

    # def create(self, validated_data):
    #     """创建应用发布, 讲客户端输入的用户名转换为id"""
    #     user = validated_data.get("user")
    #     print(user)
    #     user_info = User.objects.values(username=user)
    #     # user_id = user_info[0].id
    #     print(user_info)
    #     # validated_data["user"] = user_info.id
    #     instance = ReleaseApp.objects.create(
    #         **validated_data
    #     )
    #     return instance


class ReleaseApplyModelSerializer(serializers.ModelSerializer):
    app_name = serializers.CharField(source='release_record.release_app.name', read_only=True)
    envs_name = serializers.CharField(source='release_record.envs.name', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    # 关于git_release_commit_id只有现在选择的是git分支时才需要传递过来进行序列化器的校验，所有我们暂时不对他进行校验，回头再补充

    class Meta:
        model = ReleaseApply
        fields = ['id', 'name', 'app_name', 'envs_name', 'git_release_branch_or_tag',
                  'git_release_branch_or_tag_name', 'git_release_version', 'release_status',
                  'get_release_status_display', 'username', 'created_time', 'release_record', 'git_release_commit_id',
                  'review_user', 'review_desc']

        # branch_or_tag_choices为发布申请的状态数据
        extra_kwargs = {
            'created_time': {'read_only': True},
        }

    def create(self, validated_data):
        """
        创建发布申请
        :param validated_data:
        :return:
        """
        user_id = self.context['request'].user.id  # 用户信息
        new_obj = ReleaseApply.objects.create(**{
            "git_release_branch_or_tag": validated_data.get('git_release_branch_or_tag'),
            "git_release_version": validated_data.get('git_release_version'),
            "name": validated_data.get('name'),
            "git_release_commit_id": validated_data.get('git_release_commit_id'),
            "description": validated_data.get('description'),
            "release_record": validated_data.get('release_record'),
            "user_id": user_id,
        })

        return new_obj
