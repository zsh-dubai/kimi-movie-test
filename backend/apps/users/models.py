from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
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
