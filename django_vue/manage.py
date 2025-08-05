#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import subprocess
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_vue.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        print("Django 未安装，尝试自动安装 requirements.txt 中的依赖...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-i",
                                   "https://pypi.tuna.tsinghua.edu.cn/simple"])
            print("依赖安装完成，继续执行...")
            from django.core.management import execute_from_command_line
        except Exception as install_exc:
            raise ImportError(
                "自动安装失败，请手动运行：pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple"
            ) from install_exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
