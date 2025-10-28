from django.urls import path
from . import views

app_name = 'restaurante'

urlpatterns = [
    # Frontend view for kanban interface
    path('kanban/', views.KanbanView.as_view(), name='kanban'),
]