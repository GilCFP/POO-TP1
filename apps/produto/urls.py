from django.urls import path
from . import views

app_name = 'produto'

urlpatterns = [
    path('', views.produto_list, name='produto_list'),
    path('<int:produto_id>/', views.produto_detail, name='produto_detail'),
]
