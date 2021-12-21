import json
import os
import subprocess
from threading import Thread

from channels.generic.websocket import WebsocketConsumer
from django.conf import settings

from hippoapi.utils.key import AppSetting
from host.models import Host
from release.models import ReleaseApply


class SSHConsumer(WebsocketConsumer):
    """websocket的视图类"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = self.scope['url_route']['kwargs']['id']
        # websocket通讯的管道对象
        self.chan = None
        # 这就是基于paramiko连接远程服务器时的ssh操作对象
        self.ssh = None

    def loop_read(self):
        while True:
            data = self.chan.recv(32 * 1024)
            if not data:
                self.close(3333)
                break
            self.send(data.decode())

    #  接收客户端发送过来的指令，并发送给主机执行指令
    def receive(self, text_data=None, bytes_data=None):
        data = text_data or bytes_data
        print('receive:  xxxxxx', data, type(data))
        if data:
            self.chan.send(data + '\r\n')

    def disconnect(self, code):
        """websocket断开连接以后，服务端这边也要和远程主机关闭ssh通信"""
        self.chan.close()
        self.ssh.close()
        print('Connection close')

    # 请求来了自动触发父类connect方法，我们继承拓展父类的connect方法，因为我们和客户端建立连接的同时，就可以和客户端想要操作的主机建立一个ssh连接通道。
    def connect(self):
        print('connect连接来啦')
        self.accept()  # 建立websocket连接，进行连接的三次握手
        self._init()  # 建立和主机的ssh连接

    # 建立和主机的ssh连接
    def _init(self):
        # self.send(bytes_data=b'Connecting ...\r\n')
        self.send('Connecting ...\r\n')
        host = Host.objects.filter(pk=self.id).first()
        if not host:
            self.send(text_data='Unknown host\r\n')
            self.close()
        try:
            primary_key, public_key = AppSetting.get(settings.DEFAULT_KEY_NAME)
            self.ssh = host.get_ssh(primary_key).get_client()

        except Exception as e:
            self.send(f'Exception: {e}\r\n')
            self.close()
            return

        self.chan = self.ssh.invoke_shell(
            term='xterm')  # invoke_shell激活shell终端模式，也就是长连接模式，exec_command()函数是将服务器执行完的结果一次性返回给你；invoke_shell()函数类似shell终端，可以将执行结果分批次返回，所以我们接受数据时需要循环的取数据

        self.chan.transport.set_keepalive(30)  # 连接中没有任何信息时，该连接能够维持30秒

        # 和主机的连接一旦建立，主机就会将连接信息返回给服务端和主机的连接通道中，并且以后我们还要在这个通道中进行指令发送和指令结果的读取，所以我们开启单独的线程，去连接中一直等待和获取指令执行结果的返回数据
        Thread(target=self.loop_read).start()


def put_code_to_target(host_obj, cli, cmd_list, self):
    """推送代码到远程主机"""
    for cmd_info in cmd_list:
        self.send(cmd_info.get('msg'))
        if cmd_info.get('step') == '5':
            try:
                # 创建代码存储目录
                code, output = cli.exec_command(f"mkdir -p -m 777 {cmd_info.get('remote_dir')}")
                # 上传文件
                cli.put_file(cmd_info.get('local_path'), cmd_info.get('remote_path'))
                # 解压文件
                code, output = cli.exec_command(
                    f"cd {cmd_info.get('remote_dir')} && tar -zxf {cmd_info.get('remote_path')}")
            except Exception as e:
                error_msg = {
                    'step': cmd_info.get('step'),  # 表示自动化部署进行到第几步了
                    'error': str(e),  # 错误信息
                    'ip_addr': host_obj.ip_addr,  # 错误主机ip地址
                    'hostname': host_obj.name,  # 错误主机名称
                    'status': 1,  # status不等于0，表示有错误
                }
                error_msg_str = json.dumps(error_msg)
                self.send(error_msg_str)  # 发送错误信息
                self.close()  # 并关闭wbsocket通道
                break
        else:
            code, output = cli.exec_command(cmd_info.get('cmd'))
            if code != 0:
                # host_obj
                error_msg = {
                    'step': cmd_info.get('step'),  # 表示自动化部署进行到第几步了
                    'error': output,  # 错误信息
                    'ip_addr': host_obj.ip_addr,  # 错误主机ip地址
                    'hostname': host_obj.name,  # 错误主机名称
                    'status': 1,  # status不等于0，表示有错误
                }
                error_msg_str = json.dumps(error_msg)
                self.send(error_msg_str)  # 发送错误信息
                self.close()  # 并关闭wbsocket通道
                break


class ReleaseConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.user = self.scope['user']
        # print('SSHConsumer>>>41')
        self.id = self.scope['url_route']['kwargs']['id']
        print('>>>>id', self.id)
        # print(self.scope['url_route'])
        self.chan = None
        self.ssh = None

    def connect(self):
        print('发布连接来啦！！！！')
        self.accept()
        self._init()

    def _init(self):
        self.send('Connecting ...\r\n')
        # 查询本次发布的记录
        release_apply_obj = ReleaseApply.objects.filter(pk=self.id).first()
        release_record_obj = release_apply_obj.release_record
        # print(release_record_obj)

        # 1 检出(git clone)前的动作
        self.send('执行检出前的动作。。。')

        '''
            filefilterway   文件过滤方式
            file_filter_cmd_content  过滤的文件或目录
            before_code_check_out_value  代码检出前的指令(针对本机)
            before_release_content  代码发布前的指令(针对目标主机)
            custom_global_variable 部署运行的项目时给项目设置的全局变量
            after_code_check_out_value  代码检出后的指令(针对本机)
            after_release_value 代码发布后的指令(针对目标主机)
        '''
        code, output = subprocess.getstatusoutput(release_record_obj.before_code_check_out_value)
        if code != 0:
            error_msg = {
                'step': 1,  # 表示自动化部署进行到第几步了
                'error': output,  # 错误信息
                'status': 1,  # status不等于0，表示有错误
            }
            error_msg_str = json.dumps(error_msg)

            self.send(error_msg_str)  # 发送错误信息
            self.close()  # 并关闭wbsocket通道
            # 并还原为执行动作之前的状态（这里我就不写了）
            return code
        self.send('执行代码检出前动作完成。。。')

        # 2 检出代码
        self.send('执行代码检出中。。。')
        # git仓库地址
        git_addr = release_record_obj.code_git_addr
        # git仓库的存储目录
        git_path_name = "/".join(git_addr.split("@")[-1].replace(":", "/")[:-4].split("/")[:-1])
        # # 获取项目名称，方便后面创建文件夹和打包项目代码目录
        pro_name = git_addr.rsplit('/')[-1].split('.')[0]
        git_code_dir = settings.GIT_CODE_DIR
        git_dir_path = f'{git_code_dir}/{git_path_name}'  # '/home/moluo/Desktop/hippo/hippo_api/projects/gitee.com/mooluo_admin'
        git_pro_path = f'{git_code_dir}/{git_path_name}/{pro_name}'  # '/home/moluo/Desktop/hippo/hippo_api/projects/gitee.com/mooluo_admin/hippo'

        if os.path.exists(git_pro_path):
            code, output = subprocess.getstatusoutput(f'cd {git_pro_path} && git pull {git_addr}')
        else:
            code, output = subprocess.getstatusoutput(
                f'mkdir -p -m 777 {git_dir_path} && cd {git_dir_path} && git clone {git_addr} && cd {pro_name} && git branch -r')
        if code != 0:
            error_msg = {
                'step': 2,
                'error': output,
                'status': 1,
            }
            error_msg_str = json.dumps(error_msg)

            self.send(error_msg_str)  # 发送错误信息
            self.close()  # 并关闭wbsocket通道
            # 并还原为执行动作之前的状态（这里我就不写了）
            return code

        self.send('执行代码检出完成。。。')

        # 3 检出后动作
        self.send('执行代码检出后的动作。。。')
        code, output = subprocess.getstatusoutput(
            f'cd {git_dir_path} && {release_record_obj.after_code_check_out_value} {pro_name}.tar.gz {pro_name}')
        # code, output = subprocess.getstatusoutput(release_record_obj.after_code_check_out_value)
        if code != 0:
            error_msg = {
                'step': 3,
                'error': output,
                'status': 1,
            }
            error_msg_str = json.dumps(error_msg)
            self.send(error_msg_str)  # 发送错误信息

            self.close()  # 并关闭wbsocket通道
            # 并还原为执行动作之前的状态

        self.send('执行代码检出后的动作完成。。。')
        # 如果检出没有问题的话，代码继续往下面执行
        # self.send('执行代码发布前动作。。。')
        # 后面3步是在点击发布的时候进行的

        # 4. 发布前，对目标主机执行的动作
        release_record_detail_list = release_record_obj.release_record.all()

        # 根据本次发布查询到的主机列表
        target_host_list = []
        for record_detail in release_record_detail_list:
            target_host_list.append(record_detail.hosts)

        # 开启多线程或者线程池来并发执行多个主机的代码推送
        # 并且将推送的结果和错误保存到redis中，
        # 将代码发布前  发布  发布后的指令作为成一个列表交给线程任务
        cmd_list = [
            {'step': '4', 'cmd': release_record_obj.before_release_content, 'msg': '代码发布前动作。。。', },

            {'step': '5', 'cmd': "", 'msg': '代码发布中。。。', 'local_path': f'{git_dir_path}/{pro_name}.tar.gz',
             'remote_path': f'{release_record_obj.target_host_pub_path}/{pro_name}.tar.gz',
             'remote_dir': release_record_obj.target_host_pub_path},

            {'step': '6', 'cmd': release_record_obj.after_release_value, 'msg': '代码发布后动作。。。', }

        ]

        # print('---',target_host_list)
        # primary_key, public_key = AppSetting.get(settings.DEFAULT_KEY_NAME)
        # for host_obj in target_host_list:
        #     cli = host_obj.get_ssh(primary_key)
        #     put_code_to_target(host_obj,cli,cmd_list, self)

        primary_key, public_key = AppSetting.get(settings.DEFAULT_KEY_NAME)
        t_list = []
        for host_obj in target_host_list:
            cli = host_obj.get_ssh(primary_key)
            print(f"cli={cli}")
            t = Thread(target=put_code_to_target, args=(host_obj, cli, cmd_list, self))
            t.start()
            t_list.append(t)

        for tt in t_list:
            tt.join()

        self.send('代码发布完成！！！！')

        self.close()  # 并关闭wbsocket通道
        # 并还原为执行动作之前的状态
