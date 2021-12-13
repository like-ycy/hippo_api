from models import BaseModel, models


class Environment(BaseModel):
    """
    代码发布环境模型
    """
    tag = models.CharField(max_length=32, verbose_name='环境标识')

    class Meta:
        db_table = "hp_environment"
        verbose_name = "环境配置"
        verbose_name_plural = verbose_name
