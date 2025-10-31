"""
Data validation utilities for the database population system.

This module provides comprehensive validation for data integrity, relationship
consistency, and duplicate prevention during database population operations.
"""

from decimal import Decimal
from datetime import date, datetime
from typing import Dict, List, Any, Optional, Tuple
from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Q

from apps.restaurante.models import Restaurante, Cozinha, Caixa
from apps.produto.models import Produto, Alimento, Bebida, Combo, RestricaoAlimentar
from apps.cliente.models import Cliente
from apps.pedido.models import Pedido, ItemPedido, StatusPedido


class DataValidator:
    """
    Comprehensive data validator for database population operations.
    
    Provides validation for data integrity, relationship consistency,
    and duplicate prevention across all models.
    """
    
    def __init__(self, verbose: bool = False):
        """
        Initialize the data validator.
        
        Args:
            verbose (bool): Enable verbose output for validation results
        """
        self.verbose = verbose
        self.validation_errors = []
        self.validation_warnings = []
        
    def validate_restaurant_data(self, restaurant_data: Dict[str, Any]) -> bool:
        """
        Validate restaurant data before creation.
        
        Args:
            restaurant_data (Dict[str, Any]): Restaurant data to validate
            
        Returns:
            bool: True if validation passes, False otherwise
        """
        errors = []
        
        # Required fields validation
        required_fields = ['name', 'address', 'phone', 'email']
        for field in required_fields:
            if not restaurant_data.get(field):
                errors.append(f"Restaurant {field} is required")
        
        # Name uniqueness check
        if restaurant_data.get('name'):
            if Restaurante.objects.filter(name=restaurant_data['name']).exists():
                errors.append(f"Restaurant with name '{restaurant_data['name']}' already exists")
        
        # Email format validation
        email = restaurant_data.get('email')
        if email and '@' not in email:
            errors.append(f"Invalid email format: {email}")
        
        # Phone format validation
        phone = restaurant_data.get('phone')
        if phone and not self._validate_phone_format(phone):
            errors.append(f"Invalid phone format: {phone}")
        
        # Business hours validation
        opening_time = restaurant_data.get('opening_time')
        closing_time = restaurant_data.get('closing_time')
        if opening_time and closing_time:
            if opening_time >= closing_time:
                errors.append("Opening time must be before closing time")
        
        # Financial validation
        delivery_fee = restaurant_data.get('delivery_fee')
        if delivery_fee is not None:
            if delivery_fee < 0:
                errors.append("Delivery fee cannot be negative")
            if delivery_fee > Decimal('50.00'):
                self.validation_warnings.append(f"High delivery fee: R$ {delivery_fee}")
        
        minimum_order = restaurant_data.get('minimum_order_value')
        if minimum_order is not None:
            if minimum_order < 0:
                errors.append("Minimum order value cannot be negative")
            if minimum_order > Decimal('100.00'):
                self.validation_warnings.append(f"High minimum order: R$ {minimum_order}")
        
        if errors:
            self.validation_errors.extend(errors)
            if self.verbose:
                print(f"Restaurant validation errors: {errors}")
            return False
        
        return True
    
    def validate_product_data(self, product_data: Dict[str, Any]) -> bool:
        """
        Validate product data before creation.
        
        Args:
            product_data (Dict[str, Any]): Product data to validate
            
        Returns:
            bool: True if validation passes, False otherwise
        """
        errors = []
        
        # Required fields validation
        required_fields = ['name', 'price', 'category']
        for field in required_fields:
            if not product_data.get(field):
                errors.append(f"Product {field} is required")
        
        # Name uniqueness check (within category)
        name = product_data.get('name')
        category = product_data.get('category')
        if name and category:
            existing_product = Produto.objects.filter(
                name=name, 
                category=category
            ).first()
            if existing_product:
                errors.append(f"Product '{name}' already exists in category '{category}'")
        
        # Price validation
        price = product_data.get('price')
        if price is not None:
            if price <= 0:
                errors.append("Product price must be positive")
            if price > Decimal('500.00'):
                self.validation_warnings.append(f"High price for product '{name}': R$ {price}")
        
        # Expiration date validation
        expiration_date = product_data.get('expiration_date')
        if expiration_date:
            if expiration_date < date.today():
                errors.append(f"Expiration date cannot be in the past: {expiration_date}")
        
        # Calories validation
        calories = product_data.get('calories')
        if calories is not None:
            if calories < 0:
                errors.append("Calories cannot be negative")
            if calories > 2000:
                self.validation_warnings.append(f"High calorie count for '{name}': {calories}")
        
        # Preparation time validation
        prep_time = product_data.get('time_to_prepare')
        if prep_time is not None:
            if prep_time < 0:
                errors.append("Preparation time cannot be negative")
            if prep_time > 60:
                self.validation_warnings.append(f"Long preparation time for '{name}': {prep_time} minutes")
        
        # Weight validation
        weight = product_data.get('weight_grams')
        if weight is not None:
            if weight <= 0:
                errors.append("Weight must be positive")
            if weight > 2000:
                self.validation_warnings.append(f"Heavy product '{name}': {weight}g")
        
        if errors:
            self.validation_errors.extend(errors)
            if self.verbose:
                print(f"Product validation errors for '{name}': {errors}")
            return False
        
        return True
    
    def validate_customer_data(self, customer_data: Dict[str, Any]) -> bool:
        """
        Validate customer data before creation.
        
        Args:
            customer_data (Dict[str, Any]): Customer data to validate
            
        Returns:
            bool: True if validation passes, False otherwise
        """
        errors = []
        
        # Required fields validation
        required_fields = ['name', 'cpf']
        for field in required_fields:
            if not customer_data.get(field):
                errors.append(f"Customer {field} is required")
        
        # CPF validation
        cpf = customer_data.get('cpf')
        if cpf:
            if not self._validate_cpf(cpf):
                errors.append(f"Invalid CPF: {cpf}")
            
            # CPF uniqueness check
            if Cliente.objects.filter(cpf=cpf).exists():
                errors.append(f"Customer with CPF {cpf} already exists")
        
        # Email validation for permanent customers
        is_temporary = customer_data.get('is_temporary', False)
        email = customer_data.get('email')
        if not is_temporary and not email:
            errors.append("Permanent customers must have an email address")
        
        if email and '@' not in email:
            errors.append(f"Invalid email format: {email}")
        
        # Phone validation
        phone = customer_data.get('phone')
        if phone and not self._validate_phone_format(phone):
            errors.append(f"Invalid phone format: {phone}")
        
        # Balance validation
        balance = customer_data.get('balance')
        if balance is not None:
            if balance < 0:
                errors.append("Customer balance cannot be negative")
            if balance > Decimal('10000.00'):
                self.validation_warnings.append(f"High balance for customer: R$ {balance}")
        
        if errors:
            self.validation_errors.extend(errors)
            if self.verbose:
                print(f"Customer validation errors: {errors}")
            return False
        
        return True
    
    def validate_order_data(self, order_data: Dict[str, Any]) -> bool:
        """
        Validate order data before creation.
        
        Args:
            order_data (Dict[str, Any]): Order data to validate
            
        Returns:
            bool: True if validation passes, False otherwise
        """
        errors = []
        
        # Required fields validation
        required_fields = ['cliente', 'status', 'payment_method']
        for field in required_fields:
            if not order_data.get(field):
                errors.append(f"Order {field} is required")
        
        # Customer existence validation
        cliente = order_data.get('cliente')
        if cliente and not isinstance(cliente, Cliente):
            if not Cliente.objects.filter(id=cliente).exists():
                errors.append(f"Customer with ID {cliente} does not exist")
        
        # Status validation
        status = order_data.get('status')
        if status and status not in [choice[0] for choice in StatusPedido.choices]:
            errors.append(f"Invalid order status: {status}")
        
        # Payment method validation
        payment_method = order_data.get('payment_method')
        valid_methods = ['saldo', 'pix', 'cartao', 'dinheiro']
        if payment_method and payment_method not in valid_methods:
            errors.append(f"Invalid payment method: {payment_method}")
        
        # Total price validation
        total_price = order_data.get('total_price')
        if total_price is not None:
            if total_price < 0:
                errors.append("Order total cannot be negative")
            if total_price > Decimal('1000.00'):
                self.validation_warnings.append(f"High order total: R$ {total_price}")
        
        # Date validation
        created_at = order_data.get('created_at')
        if created_at:
            if isinstance(created_at, datetime) and created_at > datetime.now():
                errors.append("Order creation date cannot be in the future")
        
        if errors:
            self.validation_errors.extend(errors)
            if self.verbose:
                print(f"Order validation errors: {errors}")
            return False
        
        return True
    
    def validate_combo_data(self, combo: Combo, combo_items: List[Tuple[Produto, int]]) -> bool:
        """
        Validate combo data and its items.
        
        Args:
            combo (Combo): Combo instance to validate
            combo_items (List[Tuple[Produto, int]]): List of (product, quantity) tuples
            
        Returns:
            bool: True if validation passes, False otherwise
        """
        errors = []
        
        # Combo items validation
        if not combo_items:
            errors.append(f"Combo '{combo.name}' must have at least one item")
        
        total_item_price = Decimal('0.00')
        for product, quantity in combo_items:
            if quantity <= 0:
                errors.append(f"Combo item quantity must be positive: {product.name}")
            
            if not product.available:
                errors.append(f"Combo contains unavailable product: {product.name}")
            
            total_item_price += product.price * quantity
        
        # Price validation
        if combo.price > total_item_price:
            errors.append(f"Combo price (R$ {combo.price}) cannot exceed sum of items (R$ {total_item_price})")
        
        # Discount validation
        if combo.discount_percentage < 0 or combo.discount_percentage > 100:
            errors.append(f"Invalid discount percentage: {combo.discount_percentage}%")
        
        if errors:
            self.validation_errors.extend(errors)
            if self.verbose:
                print(f"Combo validation errors for '{combo.name}': {errors}")
            return False
        
        return True
    
    def check_existing_data(self, clear_existing: bool = False) -> Dict[str, int]:
        """
        Check for existing data in the database.
        
        Args:
            clear_existing (bool): Whether existing data will be cleared
            
        Returns:
            Dict[str, int]: Count of existing records by model
        """
        existing_counts = {
            'restaurants': Restaurante.objects.count(),
            'products': Produto.objects.count(),
            'customers': Cliente.objects.count(),
            'orders': Pedido.objects.count(),
            'dietary_restrictions': RestricaoAlimentar.objects.count(),
        }
        
        if self.verbose:
            print("Existing data counts:")
            for model, count in existing_counts.items():
                print(f"  {model.capitalize()}: {count}")
            
            if not clear_existing and any(existing_counts.values()):
                print("Note: Existing data will be preserved. Use --clear-existing to remove all data first.")
        
        return existing_counts
    
    def validate_data_relationships(self) -> bool:
        """
        Validate data relationships and constraints across models.
        
        Returns:
            bool: True if all relationships are valid, False otherwise
        """
        errors = []
        
        # Check for restaurants without kitchens or cashiers
        try:
            restaurants_without_kitchen = Restaurante.objects.filter(cozinha__isnull=True)
            if restaurants_without_kitchen.exists():
                errors.append(f"{restaurants_without_kitchen.count()} restaurants without kitchens")
        except Exception as e:
            self.validation_warnings.append(f"Could not validate restaurant-kitchen relationships: {str(e)}")
        
        try:
            restaurants_without_cashier = Restaurante.objects.filter(caixa__isnull=True)
            if restaurants_without_cashier.exists():
                errors.append(f"{restaurants_without_cashier.count()} restaurants without cashiers")
        except Exception as e:
            self.validation_warnings.append(f"Could not validate restaurant-cashier relationships: {str(e)}")
        
        # Check for products without restaurant associations
        products_without_restaurants = Produto.objects.filter(restaurants__isnull=True)
        if products_without_restaurants.exists():
            self.validation_warnings.append(
                f"{products_without_restaurants.count()} products not associated with any restaurant"
            )
        
        # Check for orders without items
        try:
            orders_without_items = Pedido.objects.filter(itempedido__isnull=True)
            if orders_without_items.exists():
                errors.append(f"{orders_without_items.count()} orders without items")
        except Exception as e:
            self.validation_warnings.append(f"Could not validate order-item relationships: {str(e)}")
        
        # Check for combos without items
        try:
            combos_without_items = Combo.objects.filter(comboitem__isnull=True)
            if combos_without_items.exists():
                errors.append(f"{combos_without_items.count()} combos without items")
        except Exception as e:
            self.validation_warnings.append(f"Could not validate combo-item relationships: {str(e)}")
        
        # Check for invalid order totals
        try:
            invalid_orders = []
            for order in Pedido.objects.all()[:100]:  # Sample check
                try:
                    calculated_total = sum(item.subtotal for item in order.itempedido_set.all())
                    if abs(order.total_price - calculated_total) > Decimal('0.01'):
                        invalid_orders.append(order.id)
                except Exception:
                    continue  # Skip orders with calculation issues
            
            if invalid_orders:
                errors.append(f"Orders with incorrect totals: {len(invalid_orders)} found")
        except Exception as e:
            self.validation_warnings.append(f"Could not validate order totals: {str(e)}")
        
        if errors:
            self.validation_errors.extend(errors)
            if self.verbose:
                print(f"Relationship validation errors: {errors}")
            return False
        
        if self.validation_warnings and self.verbose:
            print(f"Relationship validation warnings: {self.validation_warnings}")
        
        return True
    
    def _validate_cpf(self, cpf: str) -> bool:
        """
        Validate Brazilian CPF number using the official algorithm.
        
        Args:
            cpf (str): CPF number to validate
            
        Returns:
            bool: True if CPF is valid, False otherwise
        """
        # Remove formatting
        cpf = ''.join(filter(str.isdigit, cpf))
        
        # Check length
        if len(cpf) != 11:
            return False
        
        # Check for known invalid patterns
        if cpf in ['00000000000', '11111111111', '22222222222', '33333333333',
                   '44444444444', '55555555555', '66666666666', '77777777777',
                   '88888888888', '99999999999']:
            return False
        
        # Validate first check digit
        sum1 = sum(int(cpf[i]) * (10 - i) for i in range(9))
        digit1 = 11 - (sum1 % 11)
        if digit1 >= 10:
            digit1 = 0
        
        if int(cpf[9]) != digit1:
            return False
        
        # Validate second check digit
        sum2 = sum(int(cpf[i]) * (11 - i) for i in range(10))
        digit2 = 11 - (sum2 % 11)
        if digit2 >= 10:
            digit2 = 0
        
        return int(cpf[10]) == digit2
    
    def _validate_phone_format(self, phone: str) -> bool:
        """
        Validate Brazilian phone number format.
        
        Args:
            phone (str): Phone number to validate
            
        Returns:
            bool: True if format is valid, False otherwise
        """
        # Remove formatting
        digits = ''.join(filter(str.isdigit, phone))
        
        # Brazilian phone numbers: 10 digits (landline) or 11 digits (mobile)
        if len(digits) not in [10, 11]:
            return False
        
        # Area code validation (first 2 digits)
        area_code = digits[:2]
        valid_area_codes = ['11', '12', '13', '14', '15', '16', '17', '18', '19',  # SP
                           '21', '22', '24',  # RJ
                           '27', '28',  # ES
                           '31', '32', '33', '34', '35', '37', '38',  # MG
                           '41', '42', '43', '44', '45', '46',  # PR
                           '47', '48', '49',  # SC
                           '51', '53', '54', '55',  # RS
                           '61',  # DF
                           '62', '64',  # GO
                           '63',  # TO
                           '65', '66',  # MT
                           '67',  # MS
                           '68',  # AC
                           '69',  # RO
                           '71', '73', '74', '75', '77',  # BA
                           '79',  # SE
                           '81', '87',  # PE
                           '82',  # AL
                           '83',  # PB
                           '84',  # RN
                           '85', '88',  # CE
                           '86', '89',  # PI
                           '91', '93', '94',  # PA
                           '92', '97',  # AM
                           '95',  # RR
                           '96',  # AP
                           '98', '99']  # MA
        
        return area_code in valid_area_codes
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """
        Get a summary of validation results.
        
        Returns:
            Dict[str, Any]: Validation summary with errors and warnings
        """
        return {
            'errors': self.validation_errors.copy(),
            'warnings': self.validation_warnings.copy(),
            'error_count': len(self.validation_errors),
            'warning_count': len(self.validation_warnings),
            'has_errors': len(self.validation_errors) > 0,
            'has_warnings': len(self.validation_warnings) > 0
        }
    
    def clear_validation_results(self):
        """Clear validation errors and warnings."""
        self.validation_errors.clear()
        self.validation_warnings.clear()