from functools import lru_cache

from host.models import PkeyModel


class AppSetting():
    keys = ('public_key', 'private_key')

    @classmethod
    @lru_cache(maxsize=64)
    def get(cls, name):
        """获取秘钥对"""
        info = PkeyModel.objects.filter(name=name).first
        if not info:
            raise KeyError(f'没有这个 {name!r} 秘钥对')

        # 以元组格式，返回公私钥
        return (info.private, info.public)

    @classmethod
    def set(cls, name, private_key, public_key, description=None):
        """保存秘钥对"""
        PkeyModel.objects.update_or_create(name=name, defaults={
            'private': private_key,
            'public': public_key,
            'description': description
        })
