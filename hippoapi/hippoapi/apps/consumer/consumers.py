from threading import Thread

from channels.generic.websocket import WebsocketConsumer
from django.conf import settings

from hippoapi.utils.key import AppSetting
from host.models import Host


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

    # 结果客户端发送过来的指令，并发送给主机执行指令
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
