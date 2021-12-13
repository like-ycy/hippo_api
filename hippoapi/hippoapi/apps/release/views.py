import logging

from django.db import transaction
from rest_framework import status
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ReleaseApp
from .models import ReleaseRecord, ReleaseRecordDetail
from .serializers import ReleaseAppModelSerializer

logger = logging.getLogger("django")


class ReleaseAPIView(ListAPIView, CreateAPIView):
    """发布任务视图"""
    queryset = ReleaseApp.objects.all()
    serializer_class = ReleaseAppModelSerializer


class NewReleaseAPIView(APIView):
    """新发布任务视图"""

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
