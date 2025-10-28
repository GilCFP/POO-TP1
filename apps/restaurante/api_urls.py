from django.urls import path
from . import views

app_name = 'restaurante_api'

urlpatterns = [
    # API endpoints for kanban system
    path('kanban/orders/', views.KanbanAPIView.as_view(), name='kanban_api'),
    path('kanban/orders/<int:pedido_id>/status/', views.KanbanStatusUpdateAPIView.as_view(), name='kanban_status_update'),
    path('kanban/orders/<int:pedido_id>/advance/', views.KanbanAdvanceStatusAPIView.as_view(), name='kanban_advance_status'),
]