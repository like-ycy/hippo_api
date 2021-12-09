import paramiko
from paramiko.ssh_exception import AuthenticationException

"""
transport模式
"""

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    # 1、密码连接
    ssh.connect(hostname='192.168.174.23', username='root', password='123.com')
    # 2、秘钥连接
    # pkey = RSAKey.from_private_key(StringIO(pkey))
    # ssh.connect(hostname='192.168.174.23', username='root', pkey=pkey)
    while True:
        # 保存本次ssh的连接的回话状态
        cli = ssh.get_transport().open_session()
        # 设置回话超时时间
        cli.settimeout(120)

        command = input("请输入您要发送的指令：")
        if command == "exit":
            break
        # 发送指令
        cli.exec_command(command)
        # 接受操作指令以后，远程主机返回的结果
        stdout = cli.makefile("rb", -1)
        # 读取结果并转换编码
        content = stdout.read().decode()
        print(content)
except AuthenticationException as e:
    print(e.message)

finally:
    # 关闭连接
    ssh.close()
