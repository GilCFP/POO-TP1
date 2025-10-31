"""
Order data generator for populating the database with realistic historical orders.

This module creates diverse order patterns with realistic status progressions,
distributed across time periods, with appropriate quantities, special instructions,
and payment methods. It also handles order status history tracking.
"""

import random
from decimal import Decimal
from datetime import datetime, timedelta
from django.db import transaction
from django.utils import timezone

from apps.pedido.models import Pedido, ItemPedido, StatusPedido, HistoricoPedido
from apps.cliente.models import Cliente
from apps.produto.models import Produto, Alimento, Combo


class OrderDataGenerator:
    """
    Generator class for creating realistic order data.
    
    Creates historical orders with realistic patterns including:
    - Time distribution across business hours and days
    - Realistic order status progressions
    - Appropriate item quantities and combinations
    - Special instructions and payment methods
    - Order status history tracking
    """
    
    # Payment method distribution (realistic Brazilian preferences)
    PAYMENT_METHODS = [
        ('saldo', 0.35),    # 35% - Account balance
        ('pix', 0.30),      # 30% - PIX (very popular in Brazil)
        ('cartao', 0.25),   # 25% - Credit/debit card
        ('dinheiro', 0.10), # 10% - Cash
    ]
    
    # Order status distribution for historical orders
    STATUS_DISTRIBUTION = [
        (StatusPedido.DELIVERED, 0.70),      # 70% - Successfully delivered
        (StatusPedido.CANCELED, 0.15),       # 15% - Canceled orders
        (StatusPedido.READY, 0.05),          # 5% - Ready for pickup/delivery
        (StatusPedido.PREPARING, 0.04),      # 4% - Currently being prepared
        (StatusPedido.WAITING, 0.03),        # 3% - Waiting to be prepared
        (StatusPedido.BEING_DELIVERED, 0.02), # 2% - Out for delivery
        (StatusPedido.PENDING_PAYMENT, 0.01), # 1% - Payment pending
    ]
    
    # Special instructions for food items
    SPECIAL_INSTRUCTIONS = [
        'Sem cebola',
        'Sem tomate',
        'Sem maionese',
        'Ponto da carne bem passado',
        'Ponto da carne mal passado',
        'Extra queijo',
        'Sem pimenta',
        'Caprichar no molho',
        'Batata bem crocante',
        'Pizza bem assada',
        'Hambúrguer sem gergelim',
        'Refrigerante sem gelo',
        'Bebida bem gelada',
        'Entrega rápida por favor',
        'Deixar na portaria',
    ]
    
    # Business hours for realistic order timing
    BUSINESS_HOURS = {
        'weekday': {
            'lunch_start': 11,    # 11:00
            'lunch_end': 15,      # 15:00
            'dinner_start': 18,   # 18:00
            'dinner_end': 23,     # 23:00
        },
        'weekend': {
            'lunch_start': 11,    # 11:00
            'lunch_end': 16,      # 16:00
            'dinner_start': 18,   # 18:00
            'dinner_end': 24,     # 00:00 (midnight)
        }
    }
    
    # Peak hours with higher order probability
    PEAK_HOURS = [12, 13, 19, 20, 21]  # Lunch and dinner peaks

    def __init__(self, verbose=False):
        """
        Initialize the order data generator.
        
        Args:
            verbose (bool): Enable verbose output for debugging
        """
        self.verbose = verbose
        self.created_orders = []
        self.creation_stats = {
            'total_orders': 0,
            'orders_by_status': {},
            'orders_by_payment_method': {},
            'total_order_items': 0,
            'total_order_value': Decimal('0.00'),
            'orders_with_special_instructions': 0,
            'status_history_records': 0,
            'orders_by_time_period': {
                'morning': 0,
                'lunch': 0,
                'afternoon': 0,
                'dinner': 0,
                'late_night': 0,
            }
        }
        
        # Cache for performance
        self._customers = None
        self._products = None
        self._food_products = None
        self._combo_products = None

    def _get_customers(self):
        """Get all customers, cached for performance."""
        if self._customers is None:
            self._customers = list(Cliente.objects.filter(is_active=True))
        return self._customers

    def _get_products(self):
        """Get all available products, cached for performance."""
        if self._products is None:
            self._products = list(Produto.objects.filter(available=True))
        return self._products

    def _get_food_products(self):
        """Get food products (Alimento subclass), cached for performance."""
        if self._food_products is None:
            self._food_products = list(
                Produto.objects.filter(
                    available=True,
                    alimento__isnull=False
                ).select_related('alimento')
            )
        return self._food_products

    def _get_combo_products(self):
        """Get combo products, cached for performance."""
        if self._combo_products is None:
            self._combo_products = list(
                Produto.objects.filter(
                    available=True,
                    combo__isnull=False
                ).select_related('combo')
            )
        return self._combo_products

    def _select_payment_method(self):
        """Select a payment method based on realistic distribution."""
        rand = random.random()
        cumulative_prob = 0
        
        for method, prob in self.PAYMENT_METHODS:
            cumulative_prob += prob
            if rand <= cumulative_prob:
                return method
        
        return 'saldo'  # Fallback

    def _select_order_status(self):
        """Select an order status based on realistic distribution."""
        rand = random.random()
        cumulative_prob = 0
        
        for status, prob in self.STATUS_DISTRIBUTION:
            cumulative_prob += prob
            if rand <= cumulative_prob:
                return status
        
        return StatusPedido.DELIVERED  # Fallback

    def _generate_order_datetime(self, days_back=30):
        """
        Generate a realistic order datetime within business hours.
        
        Args:
            days_back (int): Number of days back from today to generate orders
            
        Returns:
            datetime: Random datetime within business hours
        """
        # Random day within the specified range
        base_date = timezone.now().date()
        random_days = random.randint(0, days_back)
        order_date = base_date - timedelta(days=random_days)
        
        # Determine if it's a weekday or weekend
        is_weekend = order_date.weekday() >= 5  # Saturday = 5, Sunday = 6
        hours_config = self.BUSINESS_HOURS['weekend' if is_weekend else 'weekday']
        
        # Select time period with weighted probability
        time_periods = []
        
        # Lunch period (higher probability)
        for hour in range(hours_config['lunch_start'], hours_config['lunch_end']):
            weight = 3 if hour in self.PEAK_HOURS else 1
            time_periods.extend([hour] * weight)
        
        # Dinner period (higher probability)
        for hour in range(hours_config['dinner_start'], min(hours_config['dinner_end'], 24)):
            weight = 3 if hour in self.PEAK_HOURS else 1
            time_periods.extend([hour] * weight)
        
        # Select random hour from weighted periods
        selected_hour = random.choice(time_periods)
        selected_minute = random.randint(0, 59)
        selected_second = random.randint(0, 59)
        
        # Create datetime
        order_datetime = timezone.make_aware(
            datetime.combine(
                order_date,
                datetime.min.time().replace(
                    hour=selected_hour,
                    minute=selected_minute,
                    second=selected_second
                )
            )
        )
        
        return order_datetime

    def _categorize_time_period(self, order_datetime):
        """Categorize order time into periods for statistics."""
        hour = order_datetime.hour
        
        if 6 <= hour < 11:
            return 'morning'
        elif 11 <= hour < 16:
            return 'lunch'
        elif 16 <= hour < 18:
            return 'afternoon'
        elif 18 <= hour < 23:
            return 'dinner'
        else:
            return 'late_night'

    def _generate_order_items(self, customer):
        """
        Generate realistic order items for a customer.
        
        Args:
            customer (Cliente): Customer placing the order
            
        Returns:
            list: List of tuples (product, quantity, special_instructions)
        """
        products = self._get_products()
        if not products:
            return []
        
        # Determine number of items (1-5, weighted towards fewer items)
        item_counts = [1, 1, 1, 2, 2, 3, 4, 5]  # Weighted towards 1-2 items
        num_items = random.choice(item_counts)
        
        order_items = []
        selected_products = set()
        
        for _ in range(num_items):
            # Avoid duplicate products in the same order
            available_products = [p for p in products if p.id not in selected_products]
            if not available_products:
                break
            
            # Select product with preference for food items
            if random.random() < 0.8 and self._get_food_products():
                # 80% chance to select food items
                available_food = [p for p in self._get_food_products() if p.id not in selected_products]
                if available_food:
                    product = random.choice(available_food)
                else:
                    product = random.choice(available_products)
            else:
                product = random.choice(available_products)
            
            selected_products.add(product.id)
            
            # Generate quantity (1-3, weighted towards 1)
            quantities = [1, 1, 1, 1, 2, 2, 3]  # Heavily weighted towards 1
            quantity = random.choice(quantities)
            
            # Generate special instructions (30% chance)
            special_instructions = ''
            if random.random() < 0.3:
                special_instructions = random.choice(self.SPECIAL_INSTRUCTIONS)
            
            order_items.append((product, quantity, special_instructions))
        
        return order_items

    def _calculate_estimated_delivery_time(self, order_datetime, order_items):
        """
        Calculate estimated delivery time based on preparation time.
        
        Args:
            order_datetime (datetime): When the order was placed
            order_items (list): List of order items
            
        Returns:
            datetime: Estimated delivery time
        """
        total_prep_time = 0
        
        for product, quantity, _ in order_items:
            if hasattr(product, 'alimento'):
                total_prep_time += product.alimento.time_to_prepare * quantity
            elif hasattr(product, 'combo'):
                # For combos, use the combo's preparation time method
                combo_prep_time = product.combo.get_time_to_prepare()
                total_prep_time += combo_prep_time * quantity
        
        # Add base preparation time and delivery time
        base_time = 10  # 10 minutes base time
        delivery_time = random.randint(15, 30)  # 15-30 minutes delivery
        
        total_minutes = total_prep_time + base_time + delivery_time
        
        return order_datetime + timedelta(minutes=total_minutes)

    @transaction.atomic
    def generate_orders(self, count=200, days_back=30):
        """
        Generate a specified number of historical orders.
        
        Args:
            count (int): Number of orders to create
            days_back (int): Number of days back to distribute orders
            
        Returns:
            list: List of created Order objects
        """
        if self.verbose:
            print(f"Generating {count} historical orders over {days_back} days...")
        
        customers = self._get_customers()
        if not customers:
            raise ValueError("No customers available for order generation")
        
        products = self._get_products()
        if not products:
            raise ValueError("No products available for order generation")
        
        orders = []
        
        for i in range(count):
            try:
                # Select random customer
                customer = random.choice(customers)
                
                # Generate order datetime
                order_datetime = self._generate_order_datetime(days_back)
                
                # Generate order items
                order_items = self._generate_order_items(customer)
                if not order_items:
                    continue
                
                # Select payment method and status
                payment_method = self._select_payment_method()
                final_status = self._select_order_status()
                
                # Create order
                order = Pedido.objects.create(
                    cliente=customer,
                    status=StatusPedido.ORDERING,  # Start with ordering status
                    payment_method=payment_method,
                    delivery_address=customer.address or customer.get_full_address(),
                    created_at=order_datetime,
                    updated_at=order_datetime
                )
                
                # Add items to order
                total_value = Decimal('0.00')
                for product, quantity, special_instructions in order_items:
                    item = ItemPedido.objects.create(
                        pedido=order,
                        produto=product,
                        quantidade=quantity,
                        unit_price=product.price,
                        special_instructions=special_instructions,
                        created_at=order_datetime,
                        updated_at=order_datetime
                    )
                    total_value += item.subtotal
                    
                    if special_instructions:
                        self.creation_stats['orders_with_special_instructions'] += 1
                
                # Update order total
                order.total_price = total_value
                
                # Calculate estimated delivery time
                order.estimated_delivery_time = self._calculate_estimated_delivery_time(
                    order_datetime, order_items
                )
                
                order.save()
                
                # Progress order through status changes to final status
                self._progress_order_status(order, final_status, order_datetime)
                
                orders.append(order)
                self.created_orders.append(order)
                
                # Update statistics
                self._update_order_statistics(order, order_items)
                
                if self.verbose and (i + 1) % 50 == 0:
                    print(f"  Created {i + 1}/{count} orders...")
                    
            except Exception as e:
                if self.verbose:
                    print(f"  Error creating order {i + 1}: {str(e)}")
                continue
        
        if self.verbose:
            print(f"Successfully created {len(orders)} orders")
        
        return orders

    def _progress_order_status(self, order, final_status, base_datetime):
        """
        Progress an order through realistic status changes.
        
        Args:
            order (Pedido): Order to progress
            final_status (StatusPedido): Final status to reach
            base_datetime (datetime): Base datetime for status progression
        """
        # Define status progression paths
        status_progression = [
            StatusPedido.ORDERING,
            StatusPedido.PENDING_PAYMENT,
            StatusPedido.WAITING,
            StatusPedido.PREPARING,
            StatusPedido.READY,
            StatusPedido.BEING_DELIVERED,
            StatusPedido.DELIVERED
        ]
        
        current_datetime = base_datetime
        current_status = StatusPedido.ORDERING
        
        # Handle canceled orders (can be canceled at any point)
        if final_status == StatusPedido.CANCELED:
            # Cancel at a random point in the progression
            cancel_points = [
                StatusPedido.ORDERING,
                StatusPedido.PENDING_PAYMENT,
                StatusPedido.WAITING,
                StatusPedido.PREPARING
            ]
            cancel_at = random.choice(cancel_points)
            
            # Progress to cancellation point
            for status in status_progression:
                if status == cancel_at:
                    break
                current_datetime += timedelta(minutes=random.randint(1, 10))
                self._create_status_history(order, current_status, status, current_datetime)
                current_status = status
            
            # Cancel the order
            current_datetime += timedelta(minutes=random.randint(1, 5))
            self._create_status_history(order, current_status, StatusPedido.CANCELED, current_datetime)
            order.status = StatusPedido.CANCELED
            order.updated_at = current_datetime
            order.save()
            return
        
        # Progress through normal status progression
        target_index = status_progression.index(final_status)
        
        for i, status in enumerate(status_progression[1:target_index + 1], 1):
            # Add realistic time delays between status changes
            if status == StatusPedido.PENDING_PAYMENT:
                delay = random.randint(1, 3)  # 1-3 minutes
            elif status == StatusPedido.WAITING:
                delay = random.randint(2, 10)  # 2-10 minutes
            elif status == StatusPedido.PREPARING:
                delay = random.randint(5, 20)  # 5-20 minutes
            elif status == StatusPedido.READY:
                delay = random.randint(10, 30)  # 10-30 minutes
            elif status == StatusPedido.BEING_DELIVERED:
                delay = random.randint(2, 5)   # 2-5 minutes
            elif status == StatusPedido.DELIVERED:
                delay = random.randint(15, 45)  # 15-45 minutes
            else:
                delay = random.randint(1, 5)
            
            current_datetime += timedelta(minutes=delay)
            self._create_status_history(order, current_status, status, current_datetime)
            current_status = status
        
        # Update final order status
        order.status = final_status
        order.updated_at = current_datetime
        order.save()

    def _create_status_history(self, order, old_status, new_status, timestamp):
        """
        Create a status history record.
        
        Args:
            order (Pedido): Order being updated
            old_status (StatusPedido): Previous status
            new_status (StatusPedido): New status
            timestamp (datetime): When the change occurred
        """
        # Generate realistic user names for status changes
        users = [
            'Sistema', 'Cozinha', 'Caixa', 'Entregador', 'Gerente',
            'João Silva', 'Maria Santos', 'Pedro Costa', 'Ana Oliveira'
        ]
        
        user = random.choice(users)
        
        # Generate observations for some status changes
        observations = ''
        if new_status == StatusPedido.CANCELED:
            cancel_reasons = [
                'Cancelado pelo cliente',
                'Produto indisponível',
                'Problema no pagamento',
                'Tempo de entrega excedido',
                'Solicitação do cliente'
            ]
            observations = random.choice(cancel_reasons)
        elif new_status == StatusPedido.PREPARING:
            observations = 'Pedido enviado para a cozinha'
        elif new_status == StatusPedido.READY:
            observations = 'Pedido pronto para retirada/entrega'
        
        HistoricoPedido.objects.create(
            pedido=order,
            status_anterior=old_status,
            status_novo=new_status,
            usuario=user,
            observacoes=observations,
            created_at=timestamp,
            updated_at=timestamp
        )
        
        self.creation_stats['status_history_records'] += 1

    def _update_order_statistics(self, order, order_items):
        """Update creation statistics."""
        self.creation_stats['total_orders'] += 1
        self.creation_stats['total_order_items'] += len(order_items)
        self.creation_stats['total_order_value'] += order.total_price
        
        # Update status distribution
        status = order.status
        if status not in self.creation_stats['orders_by_status']:
            self.creation_stats['orders_by_status'][status] = 0
        self.creation_stats['orders_by_status'][status] += 1
        
        # Update payment method distribution
        payment_method = order.payment_method
        if payment_method not in self.creation_stats['orders_by_payment_method']:
            self.creation_stats['orders_by_payment_method'][payment_method] = 0
        self.creation_stats['orders_by_payment_method'][payment_method] += 1
        
        # Update time period distribution
        time_period = self._categorize_time_period(order.created_at)
        self.creation_stats['orders_by_time_period'][time_period] += 1

    def get_creation_summary(self):
        """
        Get a summary of the order creation process.
        
        Returns:
            dict: Statistics about created orders
        """
        summary = self.creation_stats.copy()
        
        # Add average order value
        if summary['total_orders'] > 0:
            summary['average_order_value'] = summary['total_order_value'] / summary['total_orders']
            summary['average_items_per_order'] = summary['total_order_items'] / summary['total_orders']
        else:
            summary['average_order_value'] = Decimal('0.00')
            summary['average_items_per_order'] = 0
        
        return summary

    def clear_created_orders(self):
        """Clear the list of created orders and reset statistics."""
        self.created_orders.clear()
        self.creation_stats = {
            'total_orders': 0,
            'orders_by_status': {},
            'orders_by_payment_method': {},
            'total_order_items': 0,
            'total_order_value': Decimal('0.00'),
            'orders_with_special_instructions': 0,
            'status_history_records': 0,
            'orders_by_time_period': {
                'morning': 0,
                'lunch': 0,
                'afternoon': 0,
                'dinner': 0,
                'late_night': 0,
            }
        }
        
        # Clear caches
        self._customers = None
        self._products = None
        self._food_products = None
        self._combo_products = None

    def get_orders_by_status(self, status):
        """
        Get created orders filtered by status.
        
        Args:
            status (StatusPedido): Status to filter by
            
        Returns:
            list: Filtered list of orders
        """
        return [order for order in self.created_orders if order.status == status]

    def get_orders_by_customer(self, customer):
        """
        Get created orders for a specific customer.
        
        Args:
            customer (Cliente): Customer to filter by
            
        Returns:
            list: Filtered list of orders
        """
        return [order for order in self.created_orders if order.cliente == customer]

    def get_orders_by_date_range(self, start_date, end_date):
        """
        Get created orders within a date range.
        
        Args:
            start_date (date): Start date
            end_date (date): End date
            
        Returns:
            list: Filtered list of orders
        """
        orders = []
        for order in self.created_orders:
            order_date = order.created_at.date()
            if start_date <= order_date <= end_date:
                orders.append(order)
        return orders