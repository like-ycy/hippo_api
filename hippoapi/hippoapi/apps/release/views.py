import logging

from django.conf import settings
from django.db import transaction
from rest_framework import status
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from hippoapi.utils.git_oprations import get_git_branchs, get_git_commits
from .models import ReleaseApp
from .models import ReleaseApply
from .models import ReleaseRecord, ReleaseRecordDetail
from .serializers import ReleaseAppModelSerializer
from .serializers import ReleaseApplyModelSerializer

logger = logging.getLogger("django")


class ReleaseAPIView(ListAPIView, CreateAPIView):
    """创建应用视图"""
    queryset = ReleaseApp.objects.all()
    serializer_class = ReleaseAppModelSerializer


class NewReleaseAPIView(APIView):
    """新建发布任务视图"""

    def post(self, request):
        data = request.data
        # 发布应用的主机列表
        host_ids = data.pop('pub_target_host_choose')
        # mysql事务
        with transaction.atomic():
            sid = transaction.savepoint()  # 创建事务回滚点
            try:
                # 创建发布记录
                re_record_obj = ReleaseRecord.objects.create(**data)
                for host_id in host_ids:
                    ReleaseRecordDetail.objects.create(
                        record_id=re_record_obj.id,
                        hosts_id=host_id
                    )
            except Exception as e:
                transaction.savepoint_rollback(sid)
                # 记录日志
                error_msg = f'新建发布失败，请联系管理员,错误信息为{str(e)}'
                logger.error(error_msg)
                # 回复错误信息提示客户端
                return Response({'error': error_msg}, status=status.HTTP_507_INSUFFICIENT_STORAGE)

        return Response({'msg': 'ok'})


class ReleaseApplyViewSet(ModelViewSet):
    """发布数据展示"""
    permission_classes = [IsAuthenticated]
    queryset = ReleaseApply.objects.filter(is_show=True, is_delete=False).order_by("-id")
    serializer_class = ReleaseApplyModelSerializer


class ReleaseApplyStatusAPIView(APIView):
    """获取发布申请的状态数据"""

    def get(self, request):
        status = ReleaseApply.release_status_choices
        return Response(status)


class EnvsAppsAPIView(APIView):
    """
    获取所有的环境和应用
    """

    def get(self, request):
        # 获取环境id
        envs_id = request.query_params.get('envs_id')
        envs_apps_data = list(ReleaseRecord.objects.filter(envs_id=envs_id).values(
            'release_app__id',
            'release_app__name',
        ).distinct())  # 别忘了去重
        return Response({'envs_apps_data': envs_apps_data})


class GitBranchAPIView(APIView):
    """
    获取git分支
    """

    def get(self, request):
        # 获取git地址
        app_id = request.query_params.get('app_id')
        # 先找到该应用的新建的最新发布记录
        release_record_obj = ReleaseRecord.objects.filter(is_show=True, is_delete=False,
                                                          release_app_id=app_id).order_by('-id').first()
        git_code_dir = settings.GIT_CODE_DIR  # git代码目录
        git_remote_attr = release_record_obj.code_git_addr
        # 获取git仓库的分支数据
        git_branch_list = get_git_branchs(git_remote_attr, git_code_dir)
        # 获得branch -- master等分支的所有提交版本
        branchs_name = request.query_params.get('branchs')  # master or dev

        commits = get_git_commits(branchs_name, git_remote_attr, git_code_dir)

        return Response({
            'branch_list': git_branch_list,
            'commits': commits,
            'release_record_id': release_record_obj.id
        })
