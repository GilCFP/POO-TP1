from django.http import JsonResponse
from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from .models import Customer, GameSession
from .serializers import CustomerSerializer, GameSessionSerializer


class CustomerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing casino customers.
    Provides CRUD operations for Customer model.
    """
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Customer.objects.all()
        customer_type = self.request.query_params.get('type', None)
        if customer_type is not None:
            queryset = queryset.filter(customer_type=customer_type)
        return queryset


class GameSessionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing game sessions.
    Provides CRUD operations for GameSession model.
    """
    queryset = GameSession.objects.all()
    serializer_class = GameSessionSerializer
    permission_classes = [permissions.IsAuthenticated]


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Simple health check endpoint for the API.
    """
    return JsonResponse({
        'status': 'healthy',
        'message': 'Casino CRM API is running'
    })
