"""
Customer Controller
Handles HTTP requests and responses for customer operations.
Acts as the interface between the API and the service layer.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.http import JsonResponse
from ..services.customer_service import CustomerService
from ..serializers import CustomerSerializer


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def customer_list(request):
    """
    GET: List all customers or filter by type
    POST: Create a new customer
    """
    if request.method == 'GET':
        customer_type = request.query_params.get('type', None)
        
        if customer_type:
            customers = CustomerService.get_customers_by_type(customer_type)
        else:
            customers = CustomerService.get_all_customers()
        
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        try:
            customer = CustomerService.create_customer(request.data)
            serializer = CustomerSerializer(customer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def customer_detail(request, pk):
    """
    GET: Retrieve a specific customer
    PUT: Update a customer
    DELETE: Deactivate a customer
    """
    if request.method == 'GET':
        customer = CustomerService.get_customer_by_id(pk)
        if not customer:
            return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CustomerSerializer(customer)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        try:
            customer = CustomerService.update_customer(pk, request.data)
            if not customer:
                return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)
            
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        success = CustomerService.deactivate_customer(pk)
        if success:
            return Response({'message': 'Customer deactivated successfully'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def customer_statistics(request, pk):
    """
    GET: Get detailed statistics for a specific customer
    """
    stats = CustomerService.get_customer_statistics(pk)
    if not stats:
        return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Serialize customer data
    customer_data = CustomerSerializer(stats['customer']).data
    
    response_data = {
        'customer': customer_data,
        'statistics': {
            'total_sessions': stats['total_sessions'],
            'total_bet': float(stats['total_bet']),
            'total_won': float(stats['total_won']),
            'net_result': float(stats['net_result']),
            'average_bet': float(stats['average_bet'])
        }
    }
    
    return Response(response_data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def vip_customers(request):
    """
    GET: List all VIP customers
    """
    customers = CustomerService.get_vip_customers()
    serializer = CustomerSerializer(customers, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_last_visit(request, pk):
    """
    POST: Update customer's last visit timestamp
    """
    success = CustomerService.update_last_visit(pk)
    if success:
        return Response({'message': 'Last visit updated successfully'})
    else:
        return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)
