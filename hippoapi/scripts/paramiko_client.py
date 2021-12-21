import paramiko
from paramiko.ssh_exception import AuthenticationException

"""
prarmiko client 模式， 相当于 ssh root@192.168.174.23 'pwd'
"""
pkey = open(('/home/wang/.ssh/id_rsa'), 'r').read()

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    # 1、密码连接
    ssh.connect(hostname='192.168.174.24', username='root', password='123.com')
    # 2、秘钥连接
    # pkey = RSAKey.from_private_key(StringIO(pkey))
    # ssh.connect(hostname='192.168.174.23', username='root', pkey=pkey)
    stdin, stdout, stderr = ssh.exec_command('mkdir -p /mnt/test && ls /mnt/')
    result = stdout.read()
    print(result.decode())
    ssh.close()
except AuthenticationException as e:
    print(str(e))
    print('连接失败，请检查参数是否正确！')
#
