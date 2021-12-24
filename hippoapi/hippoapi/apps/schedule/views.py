import json
import random
from datetime import datetime, timedelta

from django_celery_beat.models import IntervalSchedule, PeriodicTask
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import TaskSchedule, TaskHost


class PeriodView(APIView):
    """获取计划任务的周期类型数据返回给客户端"""

    def get(self, request):
        data = TaskSchedule.period_way_choices
        return Response(data)


class TaskView(APIView):
    def get(self, request):
        pass

    def post(self, request):
        task_data = request.data
        period_way = request.data.get('period_way')  # 计划任务的周期类型
        hosts_ids = request.data.get('hosts')  # 计划任务的执行的远程主机列表
        task_cmd = request.data.get('task_cmd')  # 计划任务要执行的任务指令
        period_content = request.data.get('period_content')  # 计划任务的周期的时间值
        task_name = request.data.get('task_name')  # 任务名称，注意不能重复

        try:
            PeriodicTask.objects.get(name=task_name)
            task_name = f'{task_name}-{str(random.randint(1000, 9999))}'
        except:
            pass

        if period_way == 1:  # 普通周期任务，默认单位为秒，可以选择修改
            schedule, created = IntervalSchedule.objects.get_or_create(
                every=int(period_content),
                period=IntervalSchedule.SECONDS,
            )
            period_obj = PeriodicTask.objects.create(
                interval=schedule,  # we created this above.
                name=task_name,  # simply describes this periodic task.
                task='schedule_task',  # name of task.
                # task='my_task2',  # name of task.
                args=json.dumps([task_cmd, hosts_ids]),
                expires=datetime.utcnow() + timedelta(seconds=30)
            )
            period_beat = period_obj.id
        elif period_way == '2':  # 一次性任务
            period_beat = 1
            pass
        else:  # cron任务
            period_beat = 1
            pass

            # 保存任务
        task_schedule_obj = TaskSchedule.objects.create(**{
            'period_beat': period_beat,  # celery-beat的任务id值
            'period_way': period_way,
            'task_cmd': task_cmd,
            'period_content': period_content,
            'task_name': task_name,
            'period_status': '1',  # 默认为激活状态
        })

        for host_id in hosts_ids:
            TaskHost.objects.create(**{
                'tasks_id': task_schedule_obj.id,
                'hosts_id': host_id,
            })

        return Response({'errormsg': 'ok'})
