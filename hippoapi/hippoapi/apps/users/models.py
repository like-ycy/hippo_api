from django.contrib.auth.models import AbstractUser

from hippoapi.utils.models import models


class User(AbstractUser):
    mobile = models.CharField(max_length=15, verbose_name='手机号码')
    avatar = models.ImageField(upload_to='avatar/%Y', verbose_name='用户头像', null=True, blank=True)

    class Meta:
        db_table = 'hippo_user'
        verbose_name = '用户信息'
        verbose_name_plural = verbose_name
