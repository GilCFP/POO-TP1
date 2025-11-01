from django.urls import path
from . import views

app_name = 'restaurante'

urlpatterns = [
    # Frontend view for kanban interface
    path('kanban/', views.KanbanView.as_view(), name='kanban'),
    
    # Dashboard URLs
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('api/dashboard/metrics/', views.DashboardAPIView.as_view(), name='dashboard_metrics'),
    path('api/dashboard/sales-chart/', views.SalesChartAPIView.as_view(), name='sales_chart'),
    path('api/dashboard/top-products/', views.TopProductsAPIView.as_view(), name='top_products'),
]