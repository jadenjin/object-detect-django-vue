import uuid

from django.db import models


# Create your models here.

# 管理表
class SysUser(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='ID')
    username = models.CharField(max_length=32)
    password = models.TextField()
    createTime = models.DateTimeField(auto_now_add=True, db_column='create_time')
    delFlag = models.BooleanField(default=False, db_column='del_flag')

    class Meta:
        db_table = 'sys_user'


class DetectModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='ID')
    name = models.CharField(max_length=64)
    labels = models.TextField()
    path = models.CharField(max_length=255)
    note = models.CharField(max_length=255)
    createTime = models.DateTimeField(auto_now_add=True, db_column='create_time')
    delFlag = models.BooleanField(default=False, db_column='del_flag')

    class Meta:
        db_table = 'detect_model'
