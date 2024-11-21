from django.urls import re_path, path
from . import views
from ..polls.urls import app_name


app_name = 'blog'

urlpatterns = [
    re_path(r'^$', views.IndexView.as_view(), name='index'),
    # 默认接收 主键参数
    path(r'<int:pk>/', views.DetailView.as_view(), name='detail'),
    path(r'<int:pk>/tags/', views.TagsView.as_view(), name='tags'),
    path(r'<int:post_id>/tags/make/', views.make_tags, name='make'),
]