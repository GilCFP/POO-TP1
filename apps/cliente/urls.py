from django.urls import path
from . import views

app_name = 'cliente'

urlpatterns = [
    # Páginas cliente (React)
    path('login/', views.login_page, name='login_page'),
    path('register/', views.register_page, name='register_page'),
    
    # API endpoints
    path('api/', views.cliente_list, name='cliente_list'),
    
    # Autenticação e criação (API)
    path('api/create-temporary/', views.create_temporary_client, name='api_create_temporary'),
    path('api/create-permanent/', views.create_permanent_client, name='api_create_permanent'),
    path('api/login/', views.login_client, name='api_login'),
    path('api/logout/', views.logout_client, name='api_logout'),
    
    # Perfil e gestão (API)
    path('api/current/', views.get_current_client, name='api_current_client'),
    path('api/profile/update/', views.update_client_profile, name='api_update_profile'),
    path('api/convert-permanent/', views.convert_to_permanent, name='api_convert_permanent'),
]