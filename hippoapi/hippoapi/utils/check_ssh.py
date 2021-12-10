from .ssh import SSH


# 用户第一次创建连接某台主机时，校验连接信息的
def valid_ssh(hostname, port, username, password=None):
    try:
        _cli = SSH(hostname, port, username, password=str(password))
        _cli.ping()  # 测试该链接是否能够使用
    except Exception:
        return False
    return True
