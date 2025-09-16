"""
Game Session Controller
Handles HTTP requests and responses for game session operations.
Acts as the interface between the API and the service layer.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import datetime
from django.utils import timezone
from ..services.game_session_service import GameSessionService
from ..serializers import GameSessionSerializer


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def session_list(request):
    """
    GET: List all sessions or filter by customer/game_type
    POST: Create a new game session
    """
    if request.method == 'GET':
        customer_id = request.query_params.get('customer_id', None)
        game_type = request.query_params.get('game_type', None)
        active_only = request.query_params.get('active_only', 'false').lower() == 'true'
        
        if active_only:
            sessions = GameSessionService.get_active_sessions()
        elif customer_id:
            sessions = GameSessionService.get_sessions_by_customer(int(customer_id))
        elif game_type:
            sessions = GameSessionService.get_sessions_by_game_type(game_type)
        else:
            sessions = GameSessionService.get_all_sessions()
        
        serializer = GameSessionSerializer(sessions, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        try:
            session = GameSessionService.create_session(request.data)
            serializer = GameSessionSerializer(session)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def session_detail(request, pk):
    """
    GET: Retrieve a specific game session
    """
    session = GameSessionService.get_session_by_id(pk)
    if not session:
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = GameSessionSerializer(session)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def end_session(request, pk):
    """
    POST: End a game session
    """
    amount_won = request.data.get('amount_won', None)
    
    session = GameSessionService.end_session(pk, amount_won)
    if not session:
        return Response({'error': 'Session not found or already ended'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = GameSessionSerializer(session)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def customer_sessions(request, customer_id):
    """
    GET: Get all sessions for a specific customer
    """
    sessions = GameSessionService.get_sessions_by_customer(customer_id)
    serializer = GameSessionSerializer(sessions, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def active_sessions(request):
    """
    GET: Get all currently active sessions
    """
    sessions = GameSessionService.get_active_sessions()
    serializer = GameSessionSerializer(sessions, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def daily_statistics(request):
    """
    GET: Get daily gaming statistics
    Query params: date (YYYY-MM-DD format, optional - defaults to today)
    """
    date_str = request.query_params.get('date', None)
    date = None
    
    if date_str:
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)
    
    stats = GameSessionService.get_daily_statistics(date)
    
    # Convert date to string for JSON serialization
    stats['date'] = stats['date'].strftime('%Y-%m-%d')
    
    return Response(stats)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def game_type_statistics(request):
    """
    GET: Get statistics grouped by game type
    """
    stats = GameSessionService.get_game_type_statistics()
    return Response(stats)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def date_range_sessions(request):
    """
    GET: Get sessions within a date range
    Query params: start_date, end_date (YYYY-MM-DD format)
    """
    start_date_str = request.query_params.get('start_date')
    end_date_str = request.query_params.get('end_date')
    
    if not start_date_str or not end_date_str:
        return Response({'error': 'Both start_date and end_date are required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        start_date = timezone.make_aware(datetime.strptime(start_date_str, '%Y-%m-%d'))
        end_date = timezone.make_aware(datetime.strptime(end_date_str, '%Y-%m-%d'))
    except ValueError:
        return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)
    
    sessions = GameSessionService.get_sessions_by_date_range(start_date, end_date)
    serializer = GameSessionSerializer(sessions, many=True)
    return Response(serializer.data)
