"""
Restaurant data generator for creating realistic restaurant, kitchen, and cashier data.

This module provides the RestaurantDataGenerator class that creates authentic
Brazilian restaurant data with proper business configurations, kitchen setups,
and cashier systems.
"""

import random
from decimal import Decimal
from datetime import time, datetime, timedelta
from django.db import transaction
from apps.restaurante.models import Restaurante, Cozinha, Caixa, EstacaoTrabalho
from apps.produto.models import RestricaoAlimentar
from apps.core.utils.brazilian_names import get_random_surname


class RestaurantDataGenerator:
    """
    Generator class for creating realistic restaurant infrastructure data.
    
    Creates restaurants with authentic Brazilian names, realistic business hours,
    associated kitchen and cashier systems, and proper operational parameters.
    """
    
    # Brazilian restaurant name components
    RESTAURANT_TYPES = [
        'Lanchonete', 'Hamburgueria', 'Pizzaria', 'Fast Food', 'Cantina',
        'Restaurante', 'Casa de Lanches', 'Disk Entrega', 'Point', 'Burguer'
    ]
    
    RESTAURANT_NAMES = [
        'Sabor Brasileiro', 'Delícias da Casa', 'Ponto do Lanche', 'Cantinho Gostoso',
        'Sabores & Cia', 'Casa do Hambúrguer', 'Pizzaria Italiana', 'Fast Burguer',
        'Lanchonete Central', 'Disk Pizza', 'Sabor Caseiro', 'Point do Sabor',
        'Hamburgueria Artesanal', 'Cantina da Esquina', 'Delícias Express',
        'Casa da Pizza', 'Lanche Rápido', 'Sabor & Tradição', 'Point Gourmet',
        'Hamburgueria Premium', 'Pizza & Cia', 'Lanchonete Familiar'
    ]
    
    STREET_TYPES = [
        'Rua', 'Avenida', 'Travessa', 'Alameda', 'Praça', 'Largo'
    ]
    
    STREET_NAMES = [
        'das Flores', 'do Comércio', 'Central', 'da Liberdade', 'São João',
        'Presidente Vargas', 'Sete de Setembro', 'Quinze de Novembro',
        'Dom Pedro II', 'Santos Dumont', 'Tiradentes', 'da Independência',
        'do Rosário', 'da Paz', 'da Esperança', 'do Progresso', 'da Vitória',
        'São José', 'Santa Rita', 'Nossa Senhora', 'do Carmo', 'São Francisco'
    ]
    
    NEIGHBORHOODS = [
        'Centro', 'Vila Nova', 'Jardim América', 'São José', 'Santa Rita',
        'Cidade Nova', 'Alto da Boa Vista', 'Jardim Europa', 'Vila São Paulo',
        'Bairro Industrial', 'Parque das Flores', 'Conjunto Habitacional',
        'Vila Operária', 'Jardim das Palmeiras', 'Setor Comercial'
    ]
    
    CITIES = [
        'São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Salvador', 'Brasília',
        'Fortaleza', 'Recife', 'Porto Alegre', 'Manaus', 'Curitiba',
        'Goiânia', 'Belém', 'Guarulhos', 'Campinas', 'São Luís',
        'Maceió', 'Duque de Caxias', 'Natal', 'Teresina', 'São Bernardo do Campo'
    ]
    
    def __init__(self, verbose=False):
        """
        Initialize the restaurant data generator.
        
        Args:
            verbose (bool): Enable verbose output during generation
        """
        self.verbose = verbose
        self.created_restaurants = []
        self.created_kitchens = []
        self.created_cashiers = []
        self.created_restrictions = []
    
    def generate_restaurant_name(self):
        """
        Generate a realistic Brazilian restaurant name.
        
        Returns:
            str: Restaurant name combining type and descriptive name
        """
        # 70% chance of using predefined names, 30% chance of surname-based names
        if random.random() < 0.7:
            restaurant_type = random.choice(self.RESTAURANT_TYPES)
            base_name = random.choice(self.RESTAURANT_NAMES)
            return f"{restaurant_type} {base_name}"
        else:
            restaurant_type = random.choice(self.RESTAURANT_TYPES)
            surname = get_random_surname()
            return f"{restaurant_type} {surname}"
    
    def generate_address(self):
        """
        Generate a realistic Brazilian address.
        
        Returns:
            str: Complete formatted address
        """
        street_type = random.choice(self.STREET_TYPES)
        street_name = random.choice(self.STREET_NAMES)
        number = random.randint(10, 9999)
        neighborhood = random.choice(self.NEIGHBORHOODS)
        city = random.choice(self.CITIES)
        
        # Sometimes add complement
        complement = ""
        if random.random() < 0.3:
            complements = ['Loja A', 'Sala 1', 'Térreo', 'Loja 2', 'Sobreloja']
            complement = f", {random.choice(complements)}"
        
        return f"{street_type} {street_name}, {number}{complement} - {neighborhood}, {city}"
    
    def generate_phone(self):
        """
        Generate a realistic Brazilian phone number.
        
        Returns:
            str: Formatted phone number
        """
        # Brazilian mobile format: (XX) 9XXXX-XXXX
        area_codes = ['11', '21', '31', '41', '51', '61', '71', '81', '85', '87']
        area_code = random.choice(area_codes)
        
        # Mobile numbers start with 9
        first_digit = '9'
        remaining_digits = ''.join([str(random.randint(0, 9)) for _ in range(8)])
        
        return f"({area_code}) {first_digit}{remaining_digits[:4]}-{remaining_digits[4:]}"
    
    def generate_email(self, restaurant_name):
        """
        Generate a realistic email address for the restaurant.
        
        Args:
            restaurant_name (str): Restaurant name to base email on
            
        Returns:
            str: Email address
        """
        # Clean restaurant name for email
        clean_name = restaurant_name.lower()
        clean_name = clean_name.replace(' ', '').replace('&', 'e')
        clean_name = ''.join(c for c in clean_name if c.isalnum())
        
        domains = ['gmail.com', 'hotmail.com', 'yahoo.com.br', 'outlook.com', 'uol.com.br']
        domain = random.choice(domains)
        
        return f"{clean_name}@{domain}"
    
    def generate_business_hours(self):
        """
        Generate realistic business hours for a fast food restaurant.
        
        Returns:
            tuple: (opening_time, closing_time) as time objects
        """
        # Most fast food places open between 10:00-12:00
        opening_hour = random.randint(10, 12)
        opening_minute = random.choice([0, 30])
        opening_time = time(opening_hour, opening_minute)
        
        # Most close between 22:00-24:00
        closing_hour = random.randint(22, 23)
        closing_minute = random.choice([0, 30])
        closing_time = time(closing_hour, closing_minute)
        
        return opening_time, closing_time
    
    def generate_operational_params(self):
        """
        Generate realistic operational parameters for the restaurant.
        
        Returns:
            dict: Dictionary with delivery fee and minimum order value
        """
        # Delivery fees typically range from R$ 3.00 to R$ 8.00
        delivery_fee = Decimal(str(random.uniform(3.0, 8.0))).quantize(Decimal('0.01'))
        
        # Minimum order values typically range from R$ 15.00 to R$ 35.00
        min_order = Decimal(str(random.uniform(15.0, 35.0))).quantize(Decimal('0.01'))
        
        return {
            'delivery_fee': delivery_fee,
            'minimum_order_value': min_order
        }
    
    def create_kitchen_stations(self, kitchen):
        """
        Create realistic work stations for a kitchen.
        
        Args:
            kitchen (Cozinha): Kitchen instance to create stations for
            
        Returns:
            list: List of created EstacaoTrabalho instances
        """
        stations = []
        
        # Standard stations for a fast food kitchen
        station_configs = [
            {'name': 'Grill Principal', 'tipo': 'grill'},
            {'name': 'Fritadeira', 'tipo': 'fryer'},
            {'name': 'Preparo Frio', 'tipo': 'prep'},
            {'name': 'Bebidas', 'tipo': 'drinks'},
            {'name': 'Montagem', 'tipo': 'assembly'},
        ]
        
        # Add optional stations based on kitchen size
        if kitchen.number_of_stations >= 3:
            station_configs.append({'name': 'Sobremesas', 'tipo': 'dessert'})
        
        if kitchen.number_of_stations >= 4:
            station_configs.append({'name': 'Grill Secundário', 'tipo': 'grill'})
        
        # Create stations up to the kitchen's capacity
        for i, config in enumerate(station_configs[:kitchen.number_of_stations]):
            station = EstacaoTrabalho.objects.create(
                cozinha=kitchen,
                name=config['name'],
                tipo=config['tipo'],
                is_active=True
            )
            stations.append(station)
            
            if self.verbose:
                print(f"  Created station: {station.name} ({station.tipo})")
        
        return stations
    
    @transaction.atomic
    def create_restaurant(self, validator=None, duplicate_manager=None, **kwargs):
        """
        Create a single restaurant with associated kitchen and cashier systems.
        
        Args:
            validator: DataValidator instance for validation
            duplicate_manager: DuplicatePreventionManager instance
            **kwargs: Optional parameters to override defaults
            
        Returns:
            dict: Dictionary containing created restaurant, kitchen, and cashier
        """
        # Generate restaurant data
        name = kwargs.get('name', self.generate_restaurant_name())
        description = kwargs.get('description', f"Deliciosos lanches e refeições em {name}")
        address = kwargs.get('address', self.generate_address())
        phone = kwargs.get('phone', self.generate_phone())
        email = kwargs.get('email', self.generate_email(name))
        
        opening_time, closing_time = self.generate_business_hours()
        operational_params = self.generate_operational_params()
        
        restaurant_data = {
            'name': name,
            'description': description,
            'address': address,
            'phone': phone,
            'email': email,
            'is_open': True,
            'opening_time': opening_time,
            'closing_time': closing_time,
            'delivery_fee': operational_params['delivery_fee'],
            'minimum_order_value': operational_params['minimum_order_value']
        }
        
        # Check for duplicates if duplicate manager is provided
        if duplicate_manager:
            existing_restaurant = duplicate_manager.check_restaurant_duplicate(restaurant_data)
            if existing_restaurant:
                return {
                    'restaurant': duplicate_manager.handle_duplicate_restaurant(existing_restaurant, restaurant_data),
                    'kitchen': existing_restaurant.cozinha,
                    'cashier': existing_restaurant.caixa,
                    'stations': list(existing_restaurant.cozinha.estacoes.all()) if hasattr(existing_restaurant, 'cozinha') else []
                }
        
        # Validate data if validator is provided
        if validator and not validator.validate_restaurant_data(restaurant_data):
            if self.verbose:
                print(f"Validation failed for restaurant: {name}")
            return None
        
        # Create restaurant
        restaurant = Restaurante.objects.create(**restaurant_data)
        
        if self.verbose:
            print(f"Created restaurant: {restaurant.name}")
            print(f"  Address: {restaurant.address}")
            print(f"  Hours: {restaurant.opening_time} - {restaurant.closing_time}")
        
        # Create associated kitchen
        num_chefs = random.randint(2, 5)
        num_stations = random.randint(3, min(6, num_chefs + 1))
        
        kitchen = Cozinha.objects.create(
            restaurante=restaurant,
            number_of_chefs=num_chefs,
            number_of_stations=num_stations,
            is_active=True
        )
        
        if self.verbose:
            print(f"  Created kitchen: {num_chefs} chefs, {num_stations} stations")
        
        # Create work stations
        stations = self.create_kitchen_stations(kitchen)
        
        # Create associated cashier system
        initial_cash = Decimal(str(random.uniform(500.0, 2000.0))).quantize(Decimal('0.01'))
        
        cashier = Caixa.objects.create(
            restaurante=restaurant,
            total_revenue=initial_cash,
            daily_revenue=Decimal('0.00'),
            is_active=True
        )
        
        if self.verbose:
            print(f"  Created cashier: R$ {initial_cash} initial cash")
        
        # Track created objects
        self.created_restaurants.append(restaurant)
        self.created_kitchens.append(kitchen)
        self.created_cashiers.append(cashier)
        
        return {
            'restaurant': restaurant,
            'kitchen': kitchen,
            'cashier': cashier,
            'stations': stations
        }
    
    def create_dietary_restrictions(self, duplicate_manager=None):
        """
        Create common dietary restrictions if they don't exist.
        
        Args:
            duplicate_manager: DuplicatePreventionManager instance
        
        Returns:
            list: List of created or existing RestricaoAlimentar instances
        """
        restrictions_data = [
            {'name': 'Glúten', 'description': 'Contém glúten', 'icon': 'gluten'},
            {'name': 'Lactose', 'description': 'Contém lactose', 'icon': 'milk'},
            {'name': 'Vegano', 'description': 'Produto vegano', 'icon': 'leaf'},
            {'name': 'Vegetariano', 'description': 'Produto vegetariano', 'icon': 'vegetarian'},
            {'name': 'Sem Açúcar', 'description': 'Produto sem açúcar adicionado', 'icon': 'no-sugar'},
            {'name': 'Sem Gordura Trans', 'description': 'Produto sem gordura trans', 'icon': 'no-trans-fat'},
            {'name': 'Rico em Fibras', 'description': 'Produto rico em fibras', 'icon': 'fiber'},
            {'name': 'Fonte de Proteína', 'description': 'Produto fonte de proteína', 'icon': 'protein'},
            {'name': 'Sem Conservantes', 'description': 'Produto sem conservantes artificiais', 'icon': 'natural'},
            {'name': 'Orgânico', 'description': 'Produto orgânico certificado', 'icon': 'organic'}
        ]
        
        created_restrictions = []
        
        for restriction_data in restrictions_data:
            if duplicate_manager:
                restriction, created = duplicate_manager.get_or_create_dietary_restriction(
                    name=restriction_data['name'],
                    description=restriction_data['description'],
                    icon=restriction_data['icon']
                )
            else:
                restriction, created = RestricaoAlimentar.objects.get_or_create(
                    name=restriction_data['name'],
                    defaults={
                        'description': restriction_data['description'],
                        'icon': restriction_data['icon']
                    }
                )
            
            if created:
                created_restrictions.append(restriction)
                if self.verbose:
                    print(f"Created dietary restriction: {restriction.name}")
            else:
                if self.verbose:
                    print(f"Dietary restriction already exists: {restriction.name}")
        
        self.created_restrictions = created_restrictions
        return list(RestricaoAlimentar.objects.all())
    
    @transaction.atomic
    def generate_restaurants(self, count=2, validator=None, duplicate_manager=None):
        """
        Generate multiple restaurants with their infrastructure.
        
        Args:
            count (int): Number of restaurants to create
            validator: DataValidator instance for validation
            duplicate_manager: DuplicatePreventionManager instance
            
        Returns:
            list: List of dictionaries containing created restaurant data
        """
        if self.verbose:
            print(f"Generating {count} restaurants...")
        
        # First, create dietary restrictions
        self.create_dietary_restrictions(duplicate_manager=duplicate_manager)
        
        restaurants_data = []
        
        for i in range(count):
            if self.verbose:
                print(f"\nCreating restaurant {i + 1}/{count}...")
            
            restaurant_data = self.create_restaurant(
                validator=validator,
                duplicate_manager=duplicate_manager
            )
            
            if restaurant_data:  # Only add if creation was successful
                restaurants_data.append(restaurant_data)
        
        if self.verbose:
            print(f"\nSuccessfully created {len(restaurants_data)} restaurants")
            print(f"Total kitchens: {len(self.created_kitchens)}")
            print(f"Total cashiers: {len(self.created_cashiers)}")
            print(f"Total dietary restrictions: {len(self.created_restrictions)}")
        
        return restaurants_data
    
    def get_creation_summary(self):
        """
        Get a summary of all created objects.
        
        Returns:
            dict: Summary statistics of created objects
        """
        return {
            'restaurants': len(self.created_restaurants),
            'kitchens': len(self.created_kitchens),
            'cashiers': len(self.created_cashiers),
            'dietary_restrictions': len(self.created_restrictions),
            'total_stations': sum(
                kitchen.estacoes.count() for kitchen in self.created_kitchens
            )
        }