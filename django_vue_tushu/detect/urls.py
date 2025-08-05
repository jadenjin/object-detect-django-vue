from django.urls import path, re_path
from . import views

urlpatterns = [
    # 登录接口
    path('login/', views.LoginView.as_view()),
    # 注册接口
    path('signin/', views.RegistryView.as_view()),

    # 模型接口
    path('model/', views.ModelView.as_view()),

    # 检测接口
    path('detect/', views.DetectView.as_view())

]
