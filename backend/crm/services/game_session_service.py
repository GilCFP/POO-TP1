"""
Game Session Service Layer
Handles all business logic related to gaming session operations.
"""
from typing import List, Optional
from django.db.models import QuerySet, Sum
from django.utils import timezone
from datetime import datetime, timedelta
from ..models import GameSession, Customer
from ..serializers import GameSessionSerializer


class GameSessionService:
    """
    Service class for game session-related business logic.
    """
    
    @staticmethod
    def get_all_sessions() -> QuerySet[GameSession]:
        """Get all game sessions."""
        return GameSession.objects.all().order_by('-start_time')
    
    @staticmethod
    def get_session_by_id(session_id: int) -> Optional[GameSession]:
        """Get a game session by ID."""
        try:
            return GameSession.objects.get(id=session_id)
        except GameSession.DoesNotExist:
            return None
    
    @staticmethod
    def get_sessions_by_customer(customer_id: int) -> QuerySet[GameSession]:
        """Get all sessions for a specific customer."""
        return GameSession.objects.filter(customer_id=customer_id).order_by('-start_time')
    
    @staticmethod
    def get_active_sessions() -> QuerySet[GameSession]:
        """Get all currently active sessions (no end time)."""
        return GameSession.objects.filter(end_time__isnull=True).order_by('-start_time')
    
    @staticmethod
    def create_session(session_data: dict) -> GameSession:
        """Create a new game session."""
        serializer = GameSessionSerializer(data=session_data)
        if serializer.is_valid():
            session = serializer.save()
            # Update customer's last visit
            from .customer_service import CustomerService
            CustomerService.update_last_visit(session.customer.id)
            return session
        raise ValueError(f"Invalid session data: {serializer.errors}")
    
    @staticmethod
    def end_session(session_id: int, amount_won: float = None) -> Optional[GameSession]:
        """End a game session."""
        session = GameSessionService.get_session_by_id(session_id)
        if not session or session.end_time:
            return None
        
        session.end_time = timezone.now()
        if amount_won is not None:
            session.amount_won = amount_won
        session.save()
        
        # Update customer's total spent
        GameSessionService._update_customer_total_spent(session.customer.id)
        return session
    
    @staticmethod
    def get_sessions_by_date_range(start_date: datetime, end_date: datetime) -> QuerySet[GameSession]:
        """Get sessions within a date range."""
        return GameSession.objects.filter(
            start_time__gte=start_date,
            start_time__lte=end_date
        ).order_by('-start_time')
    
    @staticmethod
    def get_sessions_by_game_type(game_type: str) -> QuerySet[GameSession]:
        """Get sessions filtered by game type."""
        return GameSession.objects.filter(game_type=game_type).order_by('-start_time')
    
    @staticmethod
    def get_daily_statistics(date: datetime = None) -> dict:
        """Get daily gaming statistics."""
        if not date:
            date = timezone.now().date()
        
        start_of_day = timezone.make_aware(datetime.combine(date, datetime.min.time()))
        end_of_day = timezone.make_aware(datetime.combine(date, datetime.max.time()))
        
        sessions = GameSessionService.get_sessions_by_date_range(start_of_day, end_of_day)
        
        return {
            'date': date,
            'total_sessions': sessions.count(),
            'total_amount_bet': sessions.aggregate(Sum('amount_bet'))['amount_bet__sum'] or 0,
            'total_amount_won': sessions.aggregate(Sum('amount_won'))['amount_won__sum'] or 0,
            'unique_customers': sessions.values('customer').distinct().count(),
            'active_sessions': sessions.filter(end_time__isnull=True).count()
        }
    
    @staticmethod
    def get_game_type_statistics() -> List[dict]:
        """Get statistics grouped by game type."""
        game_types = GameSession.objects.values('game_type').distinct()
        statistics = []
        
        for game_type_dict in game_types:
            game_type = game_type_dict['game_type']
            sessions = GameSessionService.get_sessions_by_game_type(game_type)
            
            statistics.append({
                'game_type': game_type,
                'total_sessions': sessions.count(),
                'total_amount_bet': sessions.aggregate(Sum('amount_bet'))['amount_bet__sum'] or 0,
                'total_amount_won': sessions.aggregate(Sum('amount_won'))['amount_won__sum'] or 0,
                'unique_players': sessions.values('customer').distinct().count()
            })
        
        return statistics
    
    @staticmethod
    def _update_customer_total_spent(customer_id: int):
        """Private method to update customer's total spent amount."""
        try:
            customer = Customer.objects.get(id=customer_id)
            total_spent = customer.game_sessions.aggregate(Sum('amount_bet'))['amount_bet__sum'] or 0
            customer.total_spent = total_spent
            customer.save()
        except Customer.DoesNotExist:
            pass
