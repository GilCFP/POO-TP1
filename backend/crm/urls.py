"""
CRM URLs - Module/Controller/Service Architecture
Routes organized by functionality with clean separation
"""
from django.urls import path
from .views import health_check
from .controllers import customer_controller, game_session_controller

urlpatterns = [
    # Health check
    path('health/', health_check, name='health-check'),
    
    # Customer endpoints
    path('api/customers/', customer_controller.customer_list, name='customer-list'),
    path('api/customers/<int:pk>/', customer_controller.customer_detail, name='customer-detail'),
    path('api/customers/<int:pk>/statistics/', customer_controller.customer_statistics, name='customer-statistics'),
    path('api/customers/<int:pk>/update-visit/', customer_controller.update_last_visit, name='customer-update-visit'),
    path('api/customers/vip/', customer_controller.vip_customers, name='vip-customers'),
    
    # Game Session endpoints
    path('api/sessions/', game_session_controller.session_list, name='session-list'),
    path('api/sessions/<int:pk>/', game_session_controller.session_detail, name='session-detail'),
    path('api/sessions/<int:pk>/end/', game_session_controller.end_session, name='end-session'),
    path('api/sessions/active/', game_session_controller.active_sessions, name='active-sessions'),
    path('api/sessions/customer/<int:customer_id>/', game_session_controller.customer_sessions, name='customer-sessions'),
    path('api/sessions/statistics/daily/', game_session_controller.daily_statistics, name='daily-statistics'),
    path('api/sessions/statistics/game-types/', game_session_controller.game_type_statistics, name='game-type-statistics'),
    path('api/sessions/date-range/', game_session_controller.date_range_sessions, name='date-range-sessions'),
]