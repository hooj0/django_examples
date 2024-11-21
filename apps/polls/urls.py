from django.urls import path
from . import views

# 设置tag 标签 URL的命名空间
# {% url 'pons:detail' question.id %}
app_name = 'pons'

urlpatterns = [
    path('', views.index, name='index'),
    path('home', views.home, name='home'),
    path('<int:question_id>/', views.detail, name='detail'),
    path('<int:question_id>/results', views.results, name='results'),
    path('<int:question_id>/vote', views.vote, name='vote'),
]