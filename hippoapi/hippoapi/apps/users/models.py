from django.contrib.auth.models import AbstractUser

from hippoapi.utils.models import models


class User(AbstractUser):
    mobile = models.CharField(max_length=15, verbose_name='手机号码')
    avatar = models.ImageField(upload_to='avatar/%Y', verbose_name='用户头像', null=True, blank=True)

    class Meta:
        db_table = 'hippo_user'
        verbose_name = '用户信息'
        verbose_name_plural = verbose_name

# class Menu(models.Model):
#     """
#     一级菜单表
#     """
#     title = models.CharField(max_length=12)
#     weight = models.IntegerField(default=0)
#     icon = models.CharField(max_length=16, null=True, blank=True)
#
#     def __str__(self):
#         return self.title
#
#     class Meta:
#         db_table = 'hippo_menu'
#         verbose_name = '一级菜单表'
#         verbose_name_plural = verbose_name
#         unique_together = ('title', 'weight')
#
#
# class Permission(models.Model):
#     url = models.CharField(max_length=32)
#     title = models.CharField(max_length=32)
#     menus = models.ForeignKey('Menu', on_delete=models.CASCADE, null=True, blank=True)
#     parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
#
#     url_name = models.CharField(max_length=32, unique=True)
#
#     def __str__(self):
#         return self.title
#
#     class Meta:
#         db_table = 'hippo_permission'
#         verbose_name = '权限表'
#         verbose_name_plural = verbose_name
#
#
# class Role(models.Model):
#     name = models.CharField(max_length=12)
#     permissions = models.ManyToManyField(to='Permission')
#
#     def __str__(self):
#         return self.name
#
#     class Meta:
#         db_table = 'hippo_role'
#         verbose_name = '角色表'
#         verbose_name_plural = verbose_name
