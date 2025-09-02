import logging

from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from rest_framework.response import Response
from django.core.paginator import Paginator
from rest_framework.views import APIView
from django_vue import settings
from django_vue.settings import DETECT_RESULT_PATH
from .Serializer import *
from .models import *
from ultralytics import YOLO
import datetime
from django.utils import timezone
import jwt
import os

logger = logging.getLogger(__name__)

ret = {
    "data": {},
    "meta": {
        "status": 200,
        "message": "注册成功"
    }
}
upload_dir = settings.MEDIA_ROOT


# 文件上传接口
class uploadApiview(APIView):
    def post(self, request):
        response = {}
        file = request.FILES.get('file')
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, file.name)
        with open(file_path, 'wb+') as f:
            f.write(file.read())
            f.close()
        response['file'] = file.name
        response['code'] = 0
        response['msg'] = "文件上传成功！"
        return Response(data={'code': 200, 'message': '上传成功', 'data': response})


# 注册接口
class RegistryView(APIView):
    authentication_classes = []

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        if SysUser.objects.filter(username=username).exists():
            ret["meta"]["status"] = 500
            ret["meta"]["message"] = "用户已存在"
            return Response(ret)
        # 加密密码
        password = make_password(password)
        SysUser.objects.create(username=username, password=password, delFlag=False)
        logger.info("注册用户 ")
        return Response(ret)


# 登录接口
class LoginView(APIView):
    authentication_classes = []

    def post(self, request):
        ret = {"data": {}, "meta": {"status": 500, "message": "用户不存在或密码错误"}}
        try:
            username = request.data["username"]
            password = request.data["password"]

            user = SysUser.objects.filter(username=username).first()
            if not user or not check_password(password, user.password):
                return Response(ret)
            now = timezone.now()
            payload = {
                "exp": now + datetime.timedelta(days=1),  # 过期时间（UTC）
                "iat": now,  # 签发时间（UTC）
                "sub": str(user.id),  # 建议用标准claim：sub
                "username": user.username,  # 自定义claim也OK
            }
            token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
            ret["data"].update({
                "token": token,
                "username": user.username,
                "user_id": str(user.id),
                "isAdmin": 1,
            })
            ret["meta"]["status"] = 200
            ret["meta"]["message"] = "登录成功"
            logger.info(f"{user.username} 登录成功")
            return Response(ret)
        except Exception as error:
            logger.error(error)
            return Response(ret)


# 模型接口
class ModelView(APIView):
    def get(self, request):
        pageNum = request.query_params.get('pageNum', 1)
        pageSize = request.query_params.get('pageSize', 999)
        name = request.query_params.get('name', '')
        queryset = DetectModel.objects.filter(delFlag=False)
        queryset = queryset.order_by('-createTime')
        if name:
            queryset = queryset.filter(name__icontains=name)
        paginator = Paginator(queryset, pageSize)
        page_obj = paginator.get_page(pageNum)
        page_obj_dq = page_obj.object_list
        page_obj_zs = paginator.count

        ser = DetectModelSerializer(instance=page_obj_dq, many=True)
        data = ser.data
        return Response(data={'code': 200, 'zs': page_obj_zs, 'data': data})

    def post(self, request):
        ser = DetectModelSerializer(data=request.data)
        if ser.is_valid():
            ser.save()
            return Response(data={'code': 200, 'message': '添加成功'})

    def put(self, request):
        model_id = request.data.get('id')
        if not model_id:
            return Response({'code': 400, 'message': '缺少id'}, status=400)

        try:
            instance = DetectModel.objects.get(id=model_id)
        except DetectModel.DoesNotExist:
            return Response({'code': 404, 'message': '对象不存在'}, status=404)

        ser = DetectModelSerializer(instance, data=request.data)
        if ser.is_valid():
            ser.save()
            return Response({'code': 200, 'message': '修改成功'})
        return Response({'code': 400, 'message': '修改失败', 'errors': ser.errors})

    def delete(self, request):
        model_id = request.data.get('id')
        if not model_id:
            return Response({'code': 400, 'message': '缺少id'}, status=400)

        try:
            instance = DetectModel.objects.get(id=model_id)
            file_path = os.path.join(upload_dir, instance.path)
            if instance.path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    return Response({'code': 500, 'message': f'文件删除失败: {str(e)}'}, status=500)
            instance.delete()
            return Response({'code': 200, 'message': '删除成功'}, status=200)
        except DetectModel.DoesNotExist:
            return Response({'code': 404, 'message': '对象不存在'}, status=404)


# 检测接口
class DetectView(APIView):
    def post(self, request):
        file = request.FILES.get('file')
        model_path = request.data.get('model_path')
        model_path = str(os.path.join("upload", model_path))
        upload_dir = settings.DETECT_PATH
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, file.name)
        save_path = str(os.path.join(DETECT_RESULT_PATH, file.name))
        os.makedirs(DETECT_RESULT_PATH, exist_ok=True)
        with open(file_path, 'wb+') as f:
            f.write(file.read())
            f.close()
        try:
            model = YOLO(model_path)
            results = model(str(file_path))
            detections = []
            for result in results:
                result.save(filename=save_path)
                boxes = result.boxes
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxyn[0].tolist()
                    cls_id = int(box.cls[0])
                    conf = float(box.conf[0])
                    w = abs(x2 - x1)
                    h = abs(y2 - y1)
                    label = model.names[cls_id]
                    detections.append({
                        'bbox': [x1, y1, w, h],
                        'label': label,
                        'confidence': round(conf, 4)
                    })
        except Exception as e:
            logger.error(e)
            return Response(data={'code': 500, 'message': '模型异常', 'data': None})

        return Response(data={'code': 200, 'message': '检测成功', 'data': detections})
