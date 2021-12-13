from io import BytesIO

import xlwt
from django.conf import settings
from django.http.response import HttpResponse
from django.utils.encoding import escape_uri_path
from rest_framework import status
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.viewsets import ViewSet

from hippoapi.utils.key import AppSetting
from .models import HostCategory, Host
from .serializers import HostCategoryModelSeiralizer, HostModelSerializers
from .utils import read_host_excel_data


class HostCategoryListAPIView(ListAPIView, CreateAPIView):
    """主机分类列表(查看和创建)"""
    queryset = HostCategory.objects.filter(is_show=True, is_delete=False).order_by("orders", "-id").all()
    serializer_class = HostCategoryModelSeiralizer
    permission_classes = [IsAuthenticated]


class HostModelViewSet(ModelViewSet):
    """主机信息(查看和创建、修改、删除)"""
    # queryset = Host.objects.all()
    serializer_class = HostModelSerializers
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # 重写qureyset方法，补充过滤主机列表参数，获取主机列表
        category_id = self.request.query_params.get("category_id", None)
        environment_id = self.request.query_params.get("env", None)
        queryset = Host.objects
        # 有分类的查询参数，则按分类来查询
        if category_id is not None:
            queryset = queryset.filter(category_id=category_id)
        # 有环境的查询参数，则按环境来查询
        if environment_id is not None:
            queryset = queryset.filter(environment_id=environment_id)

        return queryset.all()


class HostExcelView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """从excel批量导入主机列表"""
        # 获取上传的文件
        host_excel = request.deta.get('host[]')
        default_password = request.data.get("default_password")

        # 把上传文件全部写入到字节流，就不需要保存到服务端硬盘了。
        sio = BytesIO()
        for i in host_excel:
            sio.write(i)

        data = read_host_excel_data(sio, default_password)

        return Response(data)

    def get(self, request):
        # 1 读取数据库数据
        all_host_data = Host.objects.all().values('id', 'category', 'name', 'ip_addr', 'port', 'username',
                                                  'description')

        # 2 写入excel并保存
        # 创建excel
        xls = xlwt.Workbook(encoding='utf-8')
        # 创建工作簿
        sheet = xls.add_sheet('主机数据列表')
        # 给工作簿首行写入表头
        sheet.write(0, 0, 'id')
        sheet.write(0, 1, 'category')
        sheet.write(0, 2, 'name')
        sheet.write(0, 3, 'ip_addr')
        sheet.write(0, 4, 'port')
        sheet.write(0, 5, 'username')
        sheet.write(0, 6, 'description')

        # 写入数据，从第一行开始
        excel_row = 1  # 因为表头已经占据了下标为1的首行，所以此处从下标1开始写入主机数据
        for host_obj in all_host_data:
            sheet.write(excel_row, 0, host_obj.get('id'))
            sheet.write(excel_row, 1, host_obj.get('category'))
            sheet.write(excel_row, 2, host_obj.get('name'))
            sheet.write(excel_row, 3, host_obj.get('ip_addr'))
            sheet.write(excel_row, 4, host_obj.get('port'))
            sheet.write(excel_row, 5, host_obj.get('username'))
            sheet.write(excel_row, 6, host_obj.get('description'))
            excel_row += 1

        # 将数据写入io数据流，不用在本地生成excel文件，不然效率就低了
        sio = BytesIO()
        xls.save(sio)
        sio.seek(0)

        # 3 将excel数据响应回客户端
        response = HttpResponse(sio.getvalue(), content_type='application/vnd.ms-excel')

        # 3.1 文件名称中文设置
        response['Content-Disposition'] = 'attachment; filename={}'.format(escape_uri_path('主机列表数据.xls'))
        response.write(sio.getvalue())  # 必须要给response写入一下数据，不然不生效
        return response


class HostFileView(ViewSet):
    # 实例化ssh连接，获取主机id和链接
    def dispatch(self, request, *args, **kwargs):
        # 获取url路径中的pk
        pk = kwargs.get('pk')
        host_obj = Host.objects.get(pk=pk)
        primary_key, public_key = AppSetting.get(settings.DEFAULT_KEY_NAME)
        cli = host_obj.get_ssh(primary_key)
        self.cli = cli
        ret = super().dispatch(request, *args, **kwargs)

        return ret

    def get_folders(self, request, pk):
        """获取远程主机的目录列表"""
        cmd = request.query_params.get('cmd')
        res_code, res_data = self.cli.exec_command(cmd)
        return Response([res_code, res_data])

    def upload_file(self, request, pk):
        """上传文件到远程服务器"""
        # 上传的存储目录路径
        folder_path = request.query_params.get('folder_path')
        # 上传文件
        file_obj = request.FILES.get('file')  # 前端传入上传文件的路径
        folder_path += f'/{file_obj.name}'  # 拼接路径和文件名，得到文件全路径

        try:
            self.cli.put_file_by_fl(file_obj, folder_path, self.file_upload_callback)
        except:
            return Response({'error': '文件上传失败,请联系管理员或者查看一下用户权限'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"msg": "上传文件成功"})

    def file_upload_callback(self, n, k):
        print('>>>>>>>>>>>', n, k)

    def delete_file(self, request, pk):
        """删除远程服务器的文件"""
        return Response({"msg": "ok"})

    def get_file(self, request, pk):
        """远程服务器下载文件到本地"""
        return Response({"msg": "ok"})
