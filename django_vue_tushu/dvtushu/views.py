import logging

from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from rest_framework.response import Response
from django.core.paginator import Paginator
from rest_framework.views import APIView
from django_vue_tushu import settings
from django_vue_tushu.settings import DETECT_RESULT_PATH
from .Serializer import *
from .models import *
from ultralytics import YOLO
import datetime
import jwt
import os

logger = logging.getLogger(__name__)

# 前台返回格式
ret = {
    "data": {},
    "meta": {
        "status": 200,
        "message": "注册成功"
    }
}


# 图片上传接口
class uploadApiview(APIView):
    def post(self, request):
        response = {}
        file = request.FILES.get('file')

        upload_dir = settings.MEDIA_ROOT
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
    def post(self, request):
        try:
            username = request.data["username"]
            password = request.data["password"]
            if SysUser.objects.filter(username=username).exists():
                user = SysUser.objects.filter(username=username)
                if check_password(password, user.first().password):
                    pass
                else:
                    ret["meta"]["status"] = 500
                    ret["meta"]["message"] = "用户不存在或密码错误"
                    return Response(ret)
                dict = {
                    "exp": datetime.datetime.now() + datetime.timedelta(days=1),  # 过期时间
                    "iat": datetime.datetime.now(),  # 开始时间
                    "id": str(user.first().id),
                    "username": user.first().username,
                }
                token = jwt.encode(dict, settings.SECRET_KEY, algorithm="HS256")
                ret["data"]["token"] = token
                ret["data"]["username"] = user.first().username
                ret["data"]["user_id"] = str(user.first().id)
                # 这里需要根据数据库判断是不是管理员
                ret["data"]["isAdmin"] = 1
                ret["meta"]["status"] = 200
                ret["meta"]["message"] = "登录成功"
                logger.info(user.first().username + '登录成功')
                return Response(ret)
            else:
                ret["meta"]["status"] = 500
                ret["meta"]["message"] = "用户不存在或密码错误"
                return Response(ret)
        except Exception as error:
            logger.error(error)
            ret["meta"]["status"] = 500
            ret["meta"]["message"] = "用户不存在或密码错误"
            return Response(ret)


class ModelView(APIView):
    def get(self, request):
        pageNum = request.query_params.get('pageNum', 1)
        pageSize = request.query_params.get('pageSize', 10)
        name = request.query_params.get('name', '')
        queryset = DetectModel.objects.filter(delFlag=False)
        queryset = queryset.order_by('createTime')
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


class DetectView(APIView):
    def post(self, request):
        response = {}
        file = request.FILES.get('file')

        upload_dir = settings.DETECT_PATH
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, file.name)
        save_path = os.path.join(DETECT_RESULT_PATH, file.name)
        with open(file_path, 'wb+') as f:
            f.write(file.read())
            f.close()
        model = YOLO("upload/yolo11n.pt")
        results = model(str(file_path))
        detections = []
        for result in results:
            boxes = result.boxes
            result.save(filename="result.jpg")

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
        logger.info(detections)
        return Response(data={'code': 200, 'message': '检测成功', 'data': detections})

# class TSview(APIView):
#     # 单个禁用 token 验证
#     authentication_classes = [TokenAuthtication]
#
#     def get(self, request):
#         # 获取数据集（学生模型对象）
#         students_data = Book.objects.all()
#         pageNum = request.GET.get('pageNum', '')
#         pageSize = request.GET.get('pageSize', '')
#         # 过滤
#         search_nick_term = request.GET.get('title', '')
#         if search_nick_term:
#             search_nick_term = search_nick_term.strip()
#             students_data = students_data.filter(title__icontains=search_nick_term)
#         # 自定义分页 过滤后再次分页
#         paginator = Paginator(students_data, pageSize)
#         page_obj = paginator.get_page(pageNum)
#         # 拿到分页对象
#         page_obj_dq = page_obj.object_list
#         # 拿到总数
#         page_obj_zs = paginator.count
#         # 实例化序列化器，得到序列化器对象
#         # 分页对象进行序列化
#         ser = BookInfoModelSerializermodel(instance=page_obj_dq, many=True)
#         # 调用序列化器对象的data属性方法获取转换后的数据
#         data = ser.data
#
#         # 响应数据
#         return Response(data={'code': 200, 'zs': page_obj_zs, 'data': data})
#
#     def post(self, request):
#         print(request.data)
#         # 反序列化数据
#         student = BookInfoModelSerializermodel(data=request.data)
#         # 校验不通过
#         if not student.is_valid():
#             # 返回错误信息
#             return Response(data={'code': 500, 'data': student.errors})
#         # 校验通过，保存数据
#         student.save()
#         # 响应数据
#         return Response(data={'code': 200, 'message': '增加成功', 'data': student.data})
#
#
# class Tsdetailview(APIView):
#     authentication_classes = [TokenAuthtication]
#
#     def get(self, request, pk):
#         student = Book.objects.get(pk=pk)
#         ser = BookInfoModelSerializermodel(instance=student)
#         return Response(ser.data)
#
#     # 修改一个学生的信息
#     def put(self, request, pk):
#         print(request.data)
#         instance = Book.objects.get(pk=pk)
#         ser = BookInfoModelSerializermodel(instance=instance, data=request.data)
#         if not ser.is_valid():
#             return Response(data={'code': 500, 'message': ser.errors})
#         ser.save()
#         return Response(data={'code': 200, 'message': '修改成功', 'data': ser.data})
#
#     # 删除一个学生的信息
#     def delete(self, request, pk):
#         Book.objects.get(pk=pk).delete()
#         return Response(data={'code': 200, 'message': '删除成功'})
#
#
# class Cbsview(APIView):
#     # 单个禁用 token 验证
#     authentication_classes = [TokenAuthtication]
#
#     def get(self, request):
#         # 获取数据集（学生模型对象）
#         students_data = Publish.objects.all()
#         pageNum = request.GET.get('pageNum', '')
#         pageSize = request.GET.get('pageSize', '')
#         # 过滤
#         search_nick_term = request.GET.get('name', '')
#         if search_nick_term:
#             search_nick_term = search_nick_term.strip()
#             students_data = students_data.filter(name__icontains=search_nick_term)
#         # 自定义分页 过滤后再次分页
#         paginator = Paginator(students_data, pageSize)
#         page_obj = paginator.get_page(pageNum)
#         # 拿到分页对象
#         page_obj_dq = page_obj.object_list
#         # 拿到总数
#         page_obj_zs = paginator.count
#         # 实例化序列化器，得到序列化器对象
#         # 分页对象进行序列化
#         ser = PublishSerializer(instance=page_obj_dq, many=True)
#         # 调用序列化器对象的data属性方法获取转换后的数据
#         data = ser.data
#
#         # 响应数据
#         return Response(data={'code': 200, 'zs': page_obj_zs, 'data': data})
#
#     def post(self, request):
#         print(request.data)
#         # 反序列化数据
#         student = PublishSerializer(data=request.data)
#         # 校验不通过
#         if not student.is_valid():
#             # 返回错误信息
#             return Response(data={'code': 500, 'data': student.errors})
#         # 校验通过，保存数据
#         student.save()
#         # 响应数据
#         return Response(data={'code': 200, 'message': '增加成功', 'data': student.data})
#
#
# class Cbsdetailview(APIView):
#     authentication_classes = [TokenAuthtication]
#
#     def get(self, request, pk):
#         student = Publish.objects.get(pk=pk)
#         ser = PublishSerializer(instance=student)
#         return Response(ser.data)
#
#     # 修改一个学生的信息
#     def put(self, request, pk):
#         print(request.data)
#         instance = Publish.objects.get(pk=pk)
#         ser = PublishSerializer(instance=instance, data=request.data)
#         if not ser.is_valid():
#             return Response(data={'code': 500, 'message': ser.errors})
#         ser.save()
#         return Response(data={'code': 200, 'message': '修改成功', 'data': ser.data})
#
#     # 删除一个学生的信息
#     def delete(self, request, pk):
#         Publish.objects.get(pk=pk).delete()
#         return Response(data={'code': 200, 'message': '删除成功'})
#
#
# class Zzview(APIView):
#     # 单个禁用 token 验证
#     authentication_classes = [TokenAuthtication]
#
#     def get(self, request):
#         # 获取数据集（学生模型对象）
#         students_data = Author.objects.all()
#         pageNum = request.GET.get('pageNum', '')
#         pageSize = request.GET.get('pageSize', '')
#         # 过滤
#         search_nick_term = request.GET.get('name', '')
#         if search_nick_term:
#             search_nick_term = search_nick_term.strip()
#             students_data = students_data.filter(name__icontains=search_nick_term)
#         # 自定义分页 过滤后再次分页
#         paginator = Paginator(students_data, pageSize)
#         page_obj = paginator.get_page(pageNum)
#         # 拿到分页对象
#         page_obj_dq = page_obj.object_list
#         # 拿到总数
#         page_obj_zs = paginator.count
#         # 实例化序列化器，得到序列化器对象
#         # 分页对象进行序列化
#         ser = AuthorSerializer(instance=page_obj_dq, many=True)
#         # 调用序列化器对象的data属性方法获取转换后的数据
#         data = ser.data
#
#         # 响应数据
#         return Response(data={'code': 200, 'zs': page_obj_zs, 'data': data})
#
#     def post(self, request):
#         print(request.data)
#         # 反序列化数据
#         student = AuthorSerializer(data=request.data)
#         # 校验不通过
#         if not student.is_valid():
#             # 返回错误信息
#             return Response(data={'code': 500, 'data': student.errors})
#         # 校验通过，保存数据
#         student.save()
#         # 响应数据
#         return Response(data={'code': 200, 'message': '增加成功', 'data': student.data})
#
#
# class Zzdetailview(APIView):
#     authentication_classes = [TokenAuthtication]
#
#     def get(self, request, pk):
#         student = Author.objects.get(pk=pk)
#         ser = AuthorSerializer(instance=student)
#         return Response(ser.data)
#
#     # 修改一个学生的信息
#     def put(self, request, pk):
#         print(request.data)
#         instance = Author.objects.get(pk=pk)
#         ser = AuthorSerializer(instance=instance, data=request.data)
#         if not ser.is_valid():
#             return Response(data={'code': 500, 'message': ser.errors})
#         ser.save()
#         return Response(data={'code': 200, 'message': '修改成功', 'data': ser.data})
#
#     # 删除一个学生的信息
#     def delete(self, request, pk):
#         Author.objects.get(pk=pk).delete()
#         return Response(data={'code': 200, 'message': '删除成功'})
