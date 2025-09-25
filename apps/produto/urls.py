from django.urls import path
from . import views

app_name = 'produto'

urlpatterns = [
    # Página principal do cardápio (para o frontend React)
    path('', views.produto_home, name='produto_home'),

    # Endpoints da API (se você quiser mantê-los separados)
    path('api/list/', views.produto_list, name='api_produto_list'),
    path('api/<int:produto_id>/', views.produto_detail, name='api_produto_detail'),
]