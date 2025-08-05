from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from . import models


class SysUserSerializers(ModelSerializer):
    username = serializers.CharField(read_only=True)

    class Meta:
        model = models.SysUser
        fields = '__all__'


class DetectModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DetectModel
        fields = "__all__"
