from django.conf import settings
from django.utils import timezone as datetime
from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from ronglian_sms_sdk import SmsSDK

from hippoapi.utils.key import AppSetting
from host.models import Host


class MonitorViewSet(ViewSet):
    def cpu(self, request):
        """根据当前host_id获取主机地址"""
        host_id = request.query_params.get('host')

        try:
            host = Host.objects.get(id=host_id)
        except Host.DoesNotExist:
            return Response({"errmsg": "主机错误！"})

        # 私钥连接主机执行iostat命令获取cpu状态
        private_key = AppSetting.get(settings.DEFAULT_KEY_NAME)
        cli = host.get_ssh(private_key)
        code, result = cli.exec_command("iostat -c")

        if code == 0:
            value = result.split("\n")[-5].split()[0]
        else:
            return Response({"errmsg": "主机错误！"})

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        mobile = 12510187654
        redis = get_redis_connection("monitor")

        if float(value) > 80:
            """cpu使用率大于80%，发送短信"""
            has_time = redis.ttl(f'1NF_{mobile}')
            if has_time < 0:
                self.sms("12510187654", host.ip_addr, value)
                redis.setex(f"1NF_{mobile}", settings.NF1, "90%")

        elif float(value) > 60:
            """二级预警"""
            has_time = redis.ttl(f"2NF_{mobile}")
            if has_time < 0:
                self.sms("13928835901", host.ip_addr, value)
                redis.setex(f"2NF_{mobile}", settings.NF2, "75%")

        return Response({
            "name": now,
            "value": [now, float(value)]
        })

    def sms(self, mobile, host_ip, cpu_num):
        """发送短信"""
        sdk = SmsSDK(settings.ACCID, settings.ACCTOKEN, settings.APPID)
        tid = settings.TEMID
        datas = (host_ip, cpu_num)
        resp = sdk.sendMessage(tid, mobile, datas)
