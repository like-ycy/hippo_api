import json

from django.conf import settings

from hippoapi.utils.key import AppSetting
from host.models import Host
from .main import app


@app.task(name='schedule_task')
def schedule_task(cmd, hosts_ids):
    """计划任务"""
    hosts_objs = Host.objects.filter(id__in=hosts_ids)
    result_data = []
    private_key, public_key = AppSetting.get(settings.DEFAULT_KEY_NAME)
    for host_obj in hosts_objs:
        cli = host_obj.get_ssh(private_key)
        code, result = cli.exec_command(cmd)
        result_data.append({
            'host_id': host_obj.id,
            'host': host_obj.ip_addr,
            'status': code,
            'result': result
        })
        print('>>>>', code, result)

    return json.dumps(result_data)
