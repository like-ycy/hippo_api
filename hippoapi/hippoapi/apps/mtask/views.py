from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView

from hippoapi.utils.key import AppSetting
from host.models import Host


class CmdExecView(APIView):
    def post(self, request):
        """
        执行命令
        """
        host_ids = request.data.get('host_ids')
        cmd = request.data.get('cmd')
        if host_ids and cmd:
            exec_host_list = Host.objects.filter(id__in=host_ids)
            pkey, _ = AppSetting.get(settings.DEFAULT_KEY_NAME)  # 获取ssh秘钥
            response_list = []
            for host in exec_host_list:
                cli = host.get_ssh(pkey)
                # ssh 远程执行指令
                res_code, res_data = cli.exec_command(cmd)
                # res_code为0表示ok，不为0说明指令执行有问题
                response_list.append({
                    'host_info': {
                        'id': host.id,
                        'name': host.name,
                        'ip_addr': host.ip_addr,
                        'port': host.port,
                    },
                    'res_code': res_code,
                    'res_data': res_data,
                })
            return Response(response_list)

        else:
            return Response({'error': '没有该主机或者没有输入指令'}, status=400)


from rest_framework.generics import ListAPIView, CreateAPIView
from .models import CmdTemplate, CmdTemplateCategory
from .serializers import CmdTemplateModelSerializer, CmdTemplateCategoryModelSerializer
from rest_framework.permissions import IsAuthenticated


class TemplateView(ListAPIView, CreateAPIView):
    # 获取所有执行模板
    permission_classes = [IsAuthenticated]
    queryset = CmdTemplate.objects.all()
    serializer_class = CmdTemplateModelSerializer


class TemplateCategoryView(ListAPIView, CreateAPIView):
    # 获取执行模板类别
    permission_classes = [IsAuthenticated]
    queryset = CmdTemplateCategory.objects.all()
    serializer_class = CmdTemplateCategoryModelSerializer
