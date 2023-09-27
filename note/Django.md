# Django

## 一、安装

```shell
pip install Django==2.2.* -i  https://pypi.mirrors.ustc.edu.cn/simple/
```

## 二、建立项目

shell:

```shell
projectname="项目名称"
django-admin startproject ${projectname}
```

cmd:

```cmd
set projectname="项目名称"
django-admin startproject %projectname%
```

项目目录结构:

`/project/__init__.py`:将目录视为包

`/project/settings.py`:项目的基本设置

`/project/urls.py`:项目的URL声明

`/project/wsgi.py`:WSGI兼容的web服务器为项目提供服务的入口

`/manage.py`:命令行使用程序,用于和Django项目交互

启动项目:

```shell
python manage.py runserver 0.0.0.0:9955
```

修改`settings.py`中的`ALLOWED_HOSTS=["*"]`

## 三、创建应用

```shell
python manage.py startapp myapp1
```

