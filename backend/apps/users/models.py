from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class CustomUserManager(UserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        # 直接创建用户，不传入 email
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractUser):
    email = None
    objects = CustomUserManager()
    GENDER_CHOICES = [('M', '男'), ('F', '女'), ('O', '其他')]

    nickname = models.CharField(max_length=50, blank=True, verbose_name='昵称')
    avatar = models.URLField(max_length=500, blank=True, verbose_name='头像')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    birthday = models.DateField(null=True, blank=True, verbose_name='生日')
    bio = models.TextField(max_length=500, blank=True, verbose_name='简介')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.nickname or self.username
