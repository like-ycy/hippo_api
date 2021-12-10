import traceback
from io import StringIO

import django
import os
import paramiko
from django.conf import settings
from paramiko.rsakey import RSAKey
from paramiko.ssh_exception import AuthenticationException

from host.models import PkeyModel

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hippoapi.settings.dev')
django.setup()

if __name__ == '__main__':
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        pkey = PkeyModel.objects.get(name=settings.DEFAULT_KEY_NAME).private
        pkey = RSAKey.from_private_key(StringIO(pkey))
        ssh.connect(hostname='192.168.174.23', port=22, username='root', pkey=pkey, timeout=10)
        stdin, stdout, stderr = ssh.exec_command('ls -la')
        result = stdout.read()
        print(result.decode())
        # 关闭连接
        ssh.close()
    except AuthenticationException as e:
        print(traceback.format_exc())
