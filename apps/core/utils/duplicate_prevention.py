"""
Duplicate prevention utilities for database population operations.

This module provides comprehensive duplicate detection and prevention
mechanisms to ensure data integrity during population operations.
"""

from typing import Dict, List, Any, Optional, Tuple, Union
from django.db import models, transaction
from django.db.models import Q

from apps.restaurante.models import Restaurante, Cozinha, Caixa
from apps.produto.models import Produto, Alimento, Bebida, Combo, RestricaoAlimentar
from apps.cliente.models import Cliente
from apps.pedido.models import Pedido


class DuplicatePreventionManager:
    """
    Manager for preventing duplicate data creation during population operations.
    
    Provides methods to check for existing data, handle duplicates gracefully,
    and ensure data consistency across all models.
    """
    
    def __init__(self, verbose: bool = False, append_mode: bool = False):
        """
        Initialize the duplicate prevention manager.
        
        Args:
            verbose (bool): Enable verbose output for duplicate detection
            append_mode (bool): If True, append to existing data; if False, skip duplicates
        """
        self.verbose = verbose
        self.append_mode = append_mode
        self.duplicate_stats = {
            'restaurants_skipped': 0,
            'products_skipped': 0,
            'customers_skipped': 0,
            'orders_skipped': 0,
            'dietary_restrictions_skipped': 0,
            'total_skipped': 0
        }
    
    def check_restaurant_duplicate(self, restaurant_data: Dict[str, Any]) -> Optional[Restaurante]:
        """
        Check if a restaurant with similar data already exists.
        
        Args:
            restaurant_data (Dict[str, Any]): Restaurant data to check
            
        Returns:
            Optional[Restaurante]: Existing restaurant if found, None otherwise
        """
        name = restaurant_data.get('name')
        address = restaurant_data.get('address')
        
        if not name:
            return None
        
        # Check for exact name match
        existing = Restaurante.objects.filter(name=name).first()
        if existing:
            if self.verbose:
                print(f"  Duplicate restaurant found: {name}")
            self.duplicate_stats['restaurants_skipped'] += 1
            return existing
        
        # Check for similar address (same street and number)
        if address:
            # Extract street number for comparison
            import re
            number_match = re.search(r'\d+', address)
            if number_match:
                number = number_match.group()
                similar_restaurants = Restaurante.objects.filter(
                    address__icontains=number
                ).exclude(name=name)
                
                for restaurant in similar_restaurants:
                    # Check if addresses are very similar
                    if self._addresses_similar(address, restaurant.address):
                        if self.verbose:
                            print(f"  Similar restaurant found at address: {restaurant.name}")
                        return restaurant
        
        return None
    
    def check_product_duplicate(self, product_data: Dict[str, Any]) -> Optional[Produto]:
        """
        Check if a product with similar data already exists.
        
        Args:
            product_data (Dict[str, Any]): Product data to check
            
        Returns:
            Optional[Produto]: Existing product if found, None otherwise
        """
        name = product_data.get('name')
        category = product_data.get('category')
        
        if not name or not category:
            return None
        
        # Check for exact match (name + category)
        existing = Produto.objects.filter(name=name, category=category).first()
        if existing:
            if self.verbose:
                print(f"  Duplicate product found: {name} ({category})")
            self.duplicate_stats['products_skipped'] += 1
            return existing
        
        # Check for similar names in the same category
        similar_products = Produto.objects.filter(
            category=category,
            name__icontains=name.split()[0]  # Check first word
        ).exclude(name=name)
        
        for product in similar_products:
            similarity_score = self._calculate_name_similarity(name, product.name)
            if similarity_score > 0.8:  # 80% similarity threshold
                if self.verbose:
                    print(f"  Similar product found: {product.name} (similarity: {similarity_score:.2f})")
                return product
        
        return None
    
    def check_customer_duplicate(self, customer_data: Dict[str, Any]) -> Optional[Cliente]:
        """
        Check if a customer with similar data already exists.
        
        Args:
            customer_data (Dict[str, Any]): Customer data to check
            
        Returns:
            Optional[Cliente]: Existing customer if found, None otherwise
        """
        cpf = customer_data.get('cpf')
        email = customer_data.get('email')
        phone = customer_data.get('phone')
        
        # CPF is the primary unique identifier
        if cpf:
            existing = Cliente.objects.filter(cpf=cpf).first()
            if existing:
                if self.verbose:
                    print(f"  Duplicate customer found by CPF: {cpf}")
                self.duplicate_stats['customers_skipped'] += 1
                return existing
        
        # Check by email for permanent customers
        if email:
            existing = Cliente.objects.filter(email=email).first()
            if existing:
                if self.verbose:
                    print(f"  Duplicate customer found by email: {email}")
                self.duplicate_stats['customers_skipped'] += 1
                return existing
        
        # Check by phone number
        if phone:
            # Normalize phone number for comparison
            normalized_phone = ''.join(filter(str.isdigit, phone))
            existing_customers = Cliente.objects.all()
            
            for customer in existing_customers:
                if customer.phone:
                    existing_normalized = ''.join(filter(str.isdigit, customer.phone))
                    if normalized_phone == existing_normalized:
                        if self.verbose:
                            print(f"  Duplicate customer found by phone: {phone}")
                        self.duplicate_stats['customers_skipped'] += 1
                        return customer
        
        return None
    
    def check_order_duplicate(self, order_data: Dict[str, Any]) -> Optional[Pedido]:
        """
        Check if an order with similar data already exists.
        
        Args:
            order_data (Dict[str, Any]): Order data to check
            
        Returns:
            Optional[Pedido]: Existing order if found, None otherwise
        """
        cliente = order_data.get('cliente')
        created_at = order_data.get('created_at')
        total_price = order_data.get('total_price')
        
        if not cliente or not created_at:
            return None
        
        # Check for orders from the same customer at the same time
        from datetime import timedelta
        time_window = timedelta(minutes=5)  # 5-minute window
        
        similar_orders = Pedido.objects.filter(
            cliente=cliente,
            created_at__gte=created_at - time_window,
            created_at__lte=created_at + time_window
        )
        
        if total_price:
            similar_orders = similar_orders.filter(total_price=total_price)
        
        existing = similar_orders.first()
        if existing:
            if self.verbose:
                print(f"  Duplicate order found for customer {cliente.name} at {created_at}")
            self.duplicate_stats['orders_skipped'] += 1
            return existing
        
        return None
    
    def get_or_create_dietary_restriction(
        self, 
        name: str, 
        description: str = None, 
        icon: str = None
    ) -> Tuple[RestricaoAlimentar, bool]:
        """
        Get existing dietary restriction or create new one.
        
        Args:
            name (str): Restriction name
            description (str): Restriction description
            icon (str): Restriction icon
            
        Returns:
            Tuple[RestricaoAlimentar, bool]: (restriction, created)
        """
        defaults = {}
        if description:
            defaults['description'] = description
        if icon:
            defaults['icon'] = icon
        
        restriction, created = RestricaoAlimentar.objects.get_or_create(
            name=name,
            defaults=defaults
        )
        
        if not created:
            if self.verbose:
                print(f"  Dietary restriction already exists: {name}")
            self.duplicate_stats['dietary_restrictions_skipped'] += 1
        else:
            if self.verbose:
                print(f"  Created dietary restriction: {name}")
        
        return restriction, created
    
    def handle_duplicate_restaurant(
        self, 
        existing: Restaurante, 
        new_data: Dict[str, Any]
    ) -> Restaurante:
        """
        Handle duplicate restaurant based on append mode.
        
        Args:
            existing (Restaurante): Existing restaurant
            new_data (Dict[str, Any]): New restaurant data
            
        Returns:
            Restaurante: Restaurant to use (existing or updated)
        """
        if self.append_mode:
            # Update existing restaurant with new data
            updated_fields = []
            
            for field, value in new_data.items():
                if hasattr(existing, field) and value is not None:
                    current_value = getattr(existing, field)
                    if current_value != value:
                        setattr(existing, field, value)
                        updated_fields.append(field)
            
            if updated_fields:
                existing.save()
                if self.verbose:
                    print(f"  Updated restaurant {existing.name}: {', '.join(updated_fields)}")
        
        return existing
    
    def handle_duplicate_product(
        self, 
        existing: Produto, 
        new_data: Dict[str, Any]
    ) -> Produto:
        """
        Handle duplicate product based on append mode.
        
        Args:
            existing (Produto): Existing product
            new_data (Dict[str, Any]): New product data
            
        Returns:
            Produto: Product to use (existing or updated)
        """
        if self.append_mode:
            # Update price if new price is different
            new_price = new_data.get('price')
            if new_price and existing.price != new_price:
                existing.price = new_price
                existing.save()
                if self.verbose:
                    print(f"  Updated product {existing.name} price: R$ {new_price}")
        
        return existing
    
    def handle_duplicate_customer(
        self, 
        existing: Cliente, 
        new_data: Dict[str, Any]
    ) -> Cliente:
        """
        Handle duplicate customer based on append mode.
        
        Args:
            existing (Cliente): Existing customer
            new_data (Dict[str, Any]): New customer data
            
        Returns:
            Cliente: Customer to use (existing or updated)
        """
        if self.append_mode:
            # Update balance if new balance is higher
            new_balance = new_data.get('balance')
            if new_balance and new_balance > existing.balance:
                existing.balance = new_balance
                existing.save()
                if self.verbose:
                    print(f"  Updated customer {existing.name} balance: R$ {new_balance}")
        
        return existing
    
    def clear_all_data(self, confirm: bool = False) -> Dict[str, int]:
        """
        Clear all existing data from the database.
        
        Args:
            confirm (bool): Confirmation flag to prevent accidental deletion
            
        Returns:
            Dict[str, int]: Count of deleted records by model
        """
        if not confirm:
            raise ValueError("Data clearing requires explicit confirmation")
        
        deleted_counts = {}
        
        with transaction.atomic():
            # Delete in reverse dependency order
            deleted_counts['orders'] = Pedido.objects.all().delete()[0]
            deleted_counts['customers'] = Cliente.objects.all().delete()[0]
            deleted_counts['products'] = Produto.objects.all().delete()[0]
            deleted_counts['cashiers'] = Caixa.objects.all().delete()[0]
            deleted_counts['kitchens'] = Cozinha.objects.all().delete()[0]
            deleted_counts['restaurants'] = Restaurante.objects.all().delete()[0]
            deleted_counts['dietary_restrictions'] = RestricaoAlimentar.objects.all().delete()[0]
        
        if self.verbose:
            print("Cleared existing data:")
            for model, count in deleted_counts.items():
                print(f"  {model.capitalize()}: {count} deleted")
        
        return deleted_counts
    
    def _addresses_similar(self, addr1: str, addr2: str) -> bool:
        """
        Check if two addresses are similar.
        
        Args:
            addr1 (str): First address
            addr2 (str): Second address
            
        Returns:
            bool: True if addresses are similar, False otherwise
        """
        # Normalize addresses for comparison
        import re
        
        def normalize_address(addr):
            # Remove common variations and normalize
            addr = addr.lower()
            addr = re.sub(r'[^\w\s]', ' ', addr)  # Remove punctuation
            addr = re.sub(r'\s+', ' ', addr)  # Normalize whitespace
            return addr.strip()
        
        norm1 = normalize_address(addr1)
        norm2 = normalize_address(addr2)
        
        # Extract street numbers
        num1 = re.search(r'\d+', norm1)
        num2 = re.search(r'\d+', norm2)
        
        if num1 and num2:
            # Same number indicates likely same address
            return num1.group() == num2.group()
        
        # Check for significant word overlap
        words1 = set(norm1.split())
        words2 = set(norm2.split())
        
        if len(words1) == 0 or len(words2) == 0:
            return False
        
        overlap = len(words1.intersection(words2))
        total_words = len(words1.union(words2))
        
        return overlap / total_words > 0.6  # 60% word overlap
    
    def _calculate_name_similarity(self, name1: str, name2: str) -> float:
        """
        Calculate similarity between two names using Levenshtein distance.
        
        Args:
            name1 (str): First name
            name2 (str): Second name
            
        Returns:
            float: Similarity score between 0 and 1
        """
        def levenshtein_distance(s1, s2):
            if len(s1) < len(s2):
                return levenshtein_distance(s2, s1)
            
            if len(s2) == 0:
                return len(s1)
            
            previous_row = list(range(len(s2) + 1))
            for i, c1 in enumerate(s1):
                current_row = [i + 1]
                for j, c2 in enumerate(s2):
                    insertions = previous_row[j + 1] + 1
                    deletions = current_row[j] + 1
                    substitutions = previous_row[j] + (c1 != c2)
                    current_row.append(min(insertions, deletions, substitutions))
                previous_row = current_row
            
            return previous_row[-1]
        
        # Normalize names
        name1 = name1.lower().strip()
        name2 = name2.lower().strip()
        
        if name1 == name2:
            return 1.0
        
        max_len = max(len(name1), len(name2))
        if max_len == 0:
            return 1.0
        
        distance = levenshtein_distance(name1, name2)
        return 1.0 - (distance / max_len)
    
    def get_duplicate_stats(self) -> Dict[str, Any]:
        """
        Get statistics about duplicate detection.
        
        Returns:
            Dict[str, Any]: Duplicate detection statistics
        """
        self.duplicate_stats['total_skipped'] = sum([
            self.duplicate_stats['restaurants_skipped'],
            self.duplicate_stats['products_skipped'],
            self.duplicate_stats['customers_skipped'],
            self.duplicate_stats['orders_skipped'],
            self.duplicate_stats['dietary_restrictions_skipped']
        ])
        
        return self.duplicate_stats.copy()
    
    def clear_duplicate_stats(self):
        """Clear duplicate detection statistics."""
        self.duplicate_stats = {
            'restaurants_skipped': 0,
            'products_skipped': 0,
            'customers_skipped': 0,
            'orders_skipped': 0,
            'dietary_restrictions_skipped': 0,
            'total_skipped': 0
        }