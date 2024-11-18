# django_examples
python framework django examples.

## 准备工作
1. 安装python3
   - 设置python环境变量：`python3 -m venv myvenv`
   - 激活python环境：`myvenv\Scripts\activate` 或 `source myvenv/bin/activate`
   - 退出python环境：`deactivate`
   - 安装依赖包：`pip install -r requirements.txt`
   - 启动django服务：`python manage.py runserver`
   - 访问：`http://127.0.0.1:8000/`
   - 访问：`http://127.0.0.1:8000/admin/`
   - 
2. 安装django
   - `pip install django==1.8`

## 创建项目
1. 创建项目：`django-admin startproject mysite`
   - `(myvenv) C:\Users\Name\djangogirls> django-admin startproject mysite .`
   ```
   djangogirls
      ├───manage.py
      └───mysite
      settings.py
      urls.py
      wsgi.py
      __init__.py
   ```
2. 创建应用：`python manage.py startapp blog`
3. 运行项目：`python manage.py runserver`
   - `python manage.py runserver 0:8000`
4. 访问：`http://127.0.0.1:8000/`
5. 修改配置文件：`mysite/settings.py`
   + 修改数据库配置 `DATABASES`
   + 修改时区 `TIME_ZONE = Asia/Shanghai`
   + 添加应用 `INSTALLED_APPS = [ 'blog' ]`
6. 创建数据库
   + `python manage.py migrate` 
   + `python manage.py makemigrations blog`

## 项目规范
大型项目应该使用Django的模块化设计，将功能模块化，每个模块对应一个app，每个app对应一个数据库表。
```angular2html
myproject/
│
├── manage.py
├── myproject/               # 项目配置文件夹
│   ├── __init__.py
│   ├── settings/            # 设置文件夹，用于存放不同环境下的设置
│   │   ├── base.py          # 基础设置文件
│   │   ├── development.py   # 开发环境设置
│   │   ├── production.py    # 生产环境设置
│   │   └── test.py          # 测试环境设置
│   ├── urls.py              # URL配置
│   ├── wsgi.py              # WSGI兼容的Web服务器入口
│   └── asgi.py              # ASGI兼容的Web服务器入口（如果使用异步）
│
├── apps/                    # 应用程序文件夹
│   ├── app1/                # 第一个应用程序
│   │   ├── migrations/      # 数据库迁移脚本
│   │   ├── static/          # 静态文件（如CSS, JavaScript等）
│   │   ├── templates/       # 模板文件
│   │   ├── tests.py         # 测试文件
│   │   │   ├── test_views.py
│   │   │   ├── test_forms.py
│   │   │   └── __init__.py
│   │   ├── views.py         # 视图文件
│   │   ├── models.py        # 数据模型文件
│   │   ├── admin.py         # 后台管理文件
│   │   ├── forms.py         # 表单文件
│   │   ├── serializers.py   # 序列化器（如果使用RESTful API）
│   │   ├── signals.py       # 信号处理器
│   │   ├── apps.py          # 应用配置
│   │   └── __init__.py
│   ├── app2/                # 第二个应用程序
│   └── ...
│
├── static/                  # 项目级别的静态文件
│   ├── css/
│   ├── js/
│   └── images/
├── media/                   # 用户上传的媒体文件
│   ├── profiles/
│   ├── documents/
│   └── images/
├── templates/               # 项目级别的模板文件
├── locale/                  # 国际化文件
├── fixtures/                # 初始数据或测试数据
├── scripts/                 # 脚本文件，比如数据库备份恢复等
│   ├── backup_db.sh             # 数据库备份脚本
│   ├── restore_db.sh            # 数据库恢复脚本
│   └── import_data.py           # 数据导入脚本
├── docs/                    # 文档文件
│   ├── architecture.md          # 架构设计文档
│   ├── installation.md          # 安装指南
│   ├── usage.md                 # 使用指南
│   └── api_reference.md         # API参考文档
├── .gitignore               # Git忽略文件
├── requirements.txt         # 依赖包列表
└── README.md                # 项目说明文档
```
关于这个结构的一些说明：
- 多环境设置：通过将不同的环境设置（开发、生产、测试）放在单独的文件中，可以更容易地管理和切换不同的配置。
- 应用分离：每个应用都有自己的目录，里面包含了该应用的所有相关文件。这种布局有助于保持代码的模块化，使得应用可以更容易地被复用或者独立地进行开发和测试。
- 静态和媒体文件：静态文件通常包含网站的CSS、JavaScript和图片等资源，而媒体文件则是用户上传的内容。这两类文件通常需要分开存放，以便于管理和部署。
- 国际化支持：locale 文件夹用于存放翻译文件，支持多语言的项目可以很好地利用这一结构。
- 初始数据和测试数据：fixtures 文件夹用于存放初始数据或测试数据，这对于自动化测试和初始化数据库非常有用。

### 子系统目录结构
```angular2html
apps/subsystem1/
├── __init__.py
├── config/                  # 子系统的配置文件
│   ├── __init__.py
│   ├── settings.py          # 子系统的特定设置
│   └── urls.py              # 子系统的URL配置
├── modules/                 # 功能模块文件夹
│   ├── module1/             # 第一个功能模块
│   │   ├── migrations/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── signals.py
│   │   ├── tasks.py
│   │   ├── tests/
│   │   ├── utils/
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── __init__.py
│   ├── module2/             # 第二个功能模块
│   │   ├── migrations/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── signals.py
│   │   ├── tasks.py
│   │   ├── tests/
│   │   ├── utils/
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── __init__.py
│   └── ...
├── static/                  # 子系统的静态文件
├── templates/               # 子系统的模板文件
└── __init__.py
```

### 功能模块目录结构
```angular2html
apps/subsystem1/modules/module1/
├── migrations/              # 数据库迁移脚本
├── admin.py                 # 后台管理文件
├── apps.py                  # 应用配置
├── forms.py                 # 表单文件
├── models.py                # 数据模型文件
├── serializers.py           # 序列化器（如果使用RESTful API）
├── signals.py               # 信号处理器
├── tasks.py                 # 异步任务
├── tests/                   # 测试文件
│   ├── test_models.py
│   ├── test_views.py
│   ├── test_forms.py
│   └── __init__.py
├── utils/                   # 辅助函数和工具类
├── views.py                 # 视图文件
├── urls.py                  # 模块内的URL配置
├── static/                  # 模块级别的静态文件
├── templates/               # 模块级别的模板文件
└── __init__.py
```

这个目录结构可以清晰地展示出每个模块的功能，并且每个模块都有自己的配置、静态文件、模板文件等。通过将功能模块放在单独的目录中，可以更方便地管理、测试和部署。

### URL配置
项目级别的 URL 配置文件 urls.py 应该简洁明了，主要负责将请求路由到各个子系统的 URL 配置。

#### 示例项目级别 urls.py
```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
path('admin/', admin.site.urls),
path('subsystem1/', include('apps.subsystem1.config.urls', namespace='subsystem1')),
path('subsystem2/', include('apps.subsystem2.config.urls', namespace='subsystem2')),
]
```
#### 示例子系统级别 urls.py
```python
# apps/subsystem1/config/urls.py
from django.urls import path, include

urlpatterns = [
path('module1/', include('apps.subsystem1.modules.module1.urls', namespace='module1')),
path('module2/', include('apps.subsystem1.modules.module2.urls', namespace='module2')),
]
```