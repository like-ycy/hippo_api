from conf_center.models import Environment
from hippoapi.utils.models import BaseModel, models
from ssh import SSH
from users.models import User


class HostCategory(BaseModel):
    """
    主机分类
    """

    class Meta:
        db_table = 'hp_host_category'
        verbose_name = '主机类别'
        verbose_name_plural = verbose_name


class Host(BaseModel):
    """
    主机信息
    """
    # 真正在数据库中的字段实际上叫 category_id，而category则代表了关联的哪个分类模型对象
    category = models.ForeignKey('HostCategory', on_delete=models.DO_NOTHING, verbose_name='主机类别', related_name='hc',
                                 null=True, blank=True)
    ip_addr = models.CharField(blank=True, null=True, max_length=500, verbose_name='连接地址')
    port = models.IntegerField(verbose_name='端口')
    username = models.CharField(max_length=50, verbose_name='登录用户')
    users = models.ManyToManyField(User)
    environment = models.ForeignKey(Environment, on_delete=models.DO_NOTHING, default=1, verbose_name='从属环境')

    class Meta:
        db_table = 'hp_host'
        verbose_name = '主机信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name + ':' + self.ip_addr

    def get_ssh(self, pkey=None):
        # 获取ssh连接对象
        # pkey = pkey or self.pkey
        return SSH(self.ip_addr, self.port, self.username, pkey)


class PkeyModel(BaseModel):
    """
    密钥模型
    """
    name = models.CharField(max_length=255, unique=True)  # 名称
    private = models.TextField(verbose_name="私钥")
    public = models.TextField(verbose_name="公钥")

    class Meta:
        db_table = 'hp_pkey'
        verbose_name = '密钥'
        verbose_name_plural = verbose_name

    def __repr__(self):
        return f'<Pkey {self.name}>'
