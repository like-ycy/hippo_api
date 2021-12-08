import paramiko
from paramiko.ssh_exception import AuthenticationException

"""
prarmiko client 模式， 相当于 ssh root@192.168.174.23 'pwd'
"""
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    ssh.connect(hostname='192.168.174.23', username='root', password='123.com')
    stdin, stdout, stderr = ssh.exec_command('pwd')
    result = stdout.read().decode()
    print(result)
    ssh.close()
except AuthenticationException as e:
    print(str(e))
    print('连接失败，请检查参数是否正确！')
