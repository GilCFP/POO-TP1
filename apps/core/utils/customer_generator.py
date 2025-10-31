"""
Customer data generator for populating the database with realistic Brazilian customers.

This module creates diverse customer profiles with valid CPF numbers, authentic Brazilian names,
realistic addresses and phone numbers, and appropriate account balances. It generates both
temporary and permanent customer accounts with proper dietary restriction associations.
"""

import random
from decimal import Decimal
from datetime import datetime, timedelta
from django.db import transaction
from django.utils import timezone

from apps.cliente.models import Cliente
from apps.produto.models import RestricaoAlimentar
from apps.core.utils.cpf_utils import generate_cpf, format_cpf
from apps.core.utils.brazilian_names import generate_random_name, generate_male_name, generate_female_name


class CustomerDataGenerator:
    """
    Generator class for creating realistic customer data.
    
    Creates customers with valid Brazilian CPF numbers, authentic names,
    realistic addresses, phone numbers, and account balances. Supports
    both temporary and permanent account types with dietary restrictions.
    """
    
    # Brazilian phone number area codes and patterns
    AREA_CODES = ['11', '21', '31', '41', '51', '61', '71', '81', '85']
    MOBILE_PREFIXES = ['9']
    LANDLINE_PREFIXES = ['2', '3', '4', '5']
    
    # Brazilian address patterns
    ADDRESS_PATTERNS = [
        'Rua {} {}, {} - {}, {} - CEP: {}-{}',
        'Avenida {} {}, {} - {}, {} - CEP: {}-{}',
        'Travessa {} {}, {} - {}, {} - CEP: {}-{}',
        'Alameda {} {}, {} - {}, {} - CEP: {}-{}',
    ]
    
    # Common Brazilian street names
    STREET_NAMES = [
        'das Flores', 'do Sol', 'da Paz', 'das Palmeiras', 'dos Ipês', 'da Liberdade',
        'do Comércio', 'da Independência', 'dos Bandeirantes', 'das Acácias', 'do Progresso',
        'da Esperança', 'dos Pinheiros', 'da Consolação', 'das Nações', 'do Trabalho',
        'da República', 'dos Estudantes', 'da Amizade', 'das Américas', 'do Bosque',
        'da Saudade', 'dos Girassóis', 'da Vitória', 'das Laranjeiras', 'do Paraíso'
    ]
    
    # Brazilian neighborhoods
    NEIGHBORHOODS = [
        'Centro', 'Vila Nova', 'Jardim América', 'Copacabana', 'Ipanema', 'Leblon',
        'Barra da Tijuca', 'Tijuca', 'Botafogo', 'Flamengo', 'Santa Teresa', 'Lapa',
        'Vila Madalena', 'Pinheiros', 'Itaim Bibi', 'Moema', 'Vila Olímpia', 'Brooklin',
        'Savassi', 'Funcionários', 'Lourdes', 'Santo Agostinho', 'Cidade Jardim',
        'Boa Viagem', 'Meireles', 'Aldeota', 'Batel', 'Água Verde', 'Bigorrilho'
    ]
    
    # Brazilian cities
    CITIES = [
        'São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Salvador', 'Brasília',
        'Fortaleza', 'Curitiba', 'Recife', 'Porto Alegre', 'Manaus', 'Belém',
        'Goiânia', 'Guarulhos', 'Campinas', 'São Luís', 'São Gonçalo', 'Maceió',
        'Duque de Caxias', 'Natal', 'Teresina', 'Campo Grande', 'Nova Iguaçu'
    ]
    
    # Email domains for permanent accounts
    EMAIL_DOMAINS = [
        'gmail.com', 'hotmail.com', 'yahoo.com.br', 'outlook.com', 'uol.com.br',
        'terra.com.br', 'ig.com.br', 'bol.com.br', 'globo.com', 'r7.com'
    ]

    def __init__(self, verbose=False):
        """
        Initialize the customer data generator.
        
        Args:
            verbose (bool): Enable verbose output for debugging
        """
        self.verbose = verbose
        self.created_customers = []
        self.creation_stats = {
            'total_customers': 0,
            'temporary_customers': 0,
            'permanent_customers': 0,
            'customers_with_restrictions': 0,
            'total_restrictions_assigned': 0,
            'cpf_generation_attempts': 0,
            'duplicate_cpf_skips': 0
        }
        
        # Cache dietary restrictions for performance
        self._dietary_restrictions = None

    def _get_dietary_restrictions(self):
        """Get all available dietary restrictions, cached for performance."""
        if self._dietary_restrictions is None:
            self._dietary_restrictions = list(RestricaoAlimentar.objects.all())
        return self._dietary_restrictions

    def _generate_phone_number(self):
        """Generate a realistic Brazilian phone number."""
        area_code = random.choice(self.AREA_CODES)
        
        # 70% chance of mobile, 30% landline
        if random.random() < 0.7:
            # Mobile number: (XX) 9XXXX-XXXX
            prefix = random.choice(self.MOBILE_PREFIXES)
            first_part = random.randint(1000, 9999)
            second_part = random.randint(1000, 9999)
            return f"({area_code}) {prefix}{first_part}-{second_part}"
        else:
            # Landline number: (XX) XXXX-XXXX
            prefix = random.choice(self.LANDLINE_PREFIXES)
            first_part = random.randint(100, 999)
            second_part = random.randint(1000, 9999)
            return f"({area_code}) {prefix}{first_part}-{second_part}"

    def _generate_address(self):
        """Generate a realistic Brazilian address."""
        pattern = random.choice(self.ADDRESS_PATTERNS)
        street_name = random.choice(self.STREET_NAMES)
        number = random.randint(1, 9999)
        complement = random.choice(['Apto 101', 'Casa', 'Bloco A', 'Sala 201', ''])
        neighborhood = random.choice(self.NEIGHBORHOODS)
        city = random.choice(self.CITIES)
        cep_first = random.randint(10000, 99999)
        cep_second = random.randint(100, 999)
        
        return pattern.format(
            street_name, number, complement, neighborhood, city, cep_first, cep_second
        ).replace(', ,', ',').replace('  ', ' ').strip()

    def _generate_email(self, name):
        """Generate an email address based on the customer name."""
        # Clean and format name for email
        name_parts = name.lower().split()
        first_name = name_parts[0]
        last_name = name_parts[-1] if len(name_parts) > 1 else ''
        
        # Remove accents and special characters
        import unicodedata
        first_name = unicodedata.normalize('NFD', first_name).encode('ascii', 'ignore').decode('ascii')
        last_name = unicodedata.normalize('NFD', last_name).encode('ascii', 'ignore').decode('ascii')
        
        # Generate email patterns
        patterns = [
            f"{first_name}.{last_name}",
            f"{first_name}{last_name}",
            f"{first_name}_{last_name}",
            f"{first_name}{random.randint(1, 999)}",
            f"{first_name}.{last_name}{random.randint(1, 99)}",
        ]
        
        email_user = random.choice(patterns)
        domain = random.choice(self.EMAIL_DOMAINS)
        
        return f"{email_user}@{domain}"

    def _generate_balance(self, is_temporary):
        """Generate a realistic account balance."""
        if is_temporary:
            # Temporary accounts typically have lower balances
            balance_ranges = [
                (0, 0, 0.3),      # 30% chance of zero balance
                (5, 50, 0.4),     # 40% chance of small balance
                (51, 150, 0.25),  # 25% chance of medium balance
                (151, 300, 0.05), # 5% chance of higher balance
            ]
        else:
            # Permanent accounts typically have higher balances
            balance_ranges = [
                (0, 0, 0.1),       # 10% chance of zero balance
                (10, 100, 0.3),    # 30% chance of small balance
                (101, 300, 0.4),   # 40% chance of medium balance
                (301, 500, 0.15),  # 15% chance of high balance
                (501, 1000, 0.05), # 5% chance of very high balance
            ]
        
        # Select balance range based on probability
        rand = random.random()
        cumulative_prob = 0
        
        for min_val, max_val, prob in balance_ranges:
            cumulative_prob += prob
            if rand <= cumulative_prob:
                if min_val == max_val == 0:
                    return Decimal('0.00')
                return Decimal(str(round(random.uniform(min_val, max_val), 2)))
        
        # Fallback
        return Decimal('50.00')

    def _assign_dietary_restrictions(self, customer):
        """Assign dietary restrictions to a customer."""
        restrictions = self._get_dietary_restrictions()
        if not restrictions:
            return 0
        
        # 30% chance of having dietary restrictions
        if random.random() > 0.3:
            return 0
        
        # Number of restrictions (1-3, weighted towards fewer)
        restriction_counts = [1, 1, 1, 2, 2, 3]  # Weighted towards 1-2 restrictions
        num_restrictions = random.choice(restriction_counts)
        
        # Select random restrictions
        selected_restrictions = random.sample(
            restrictions, 
            min(num_restrictions, len(restrictions))
        )
        
        # Assign restrictions to customer
        customer.dietary_restrictions.set(selected_restrictions)
        
        if self.verbose:
            restriction_names = [r.name for r in selected_restrictions]
            print(f"    Assigned restrictions: {', '.join(restriction_names)}")
        
        return len(selected_restrictions)

    def _generate_unique_cpf(self, max_attempts=100):
        """Generate a unique CPF that doesn't exist in the database."""
        for attempt in range(max_attempts):
            self.creation_stats['cpf_generation_attempts'] += 1
            cpf = generate_cpf()
            formatted_cpf = format_cpf(cpf)
            
            # Check if CPF already exists
            if not Cliente.objects.filter(cpf=formatted_cpf).exists():
                return formatted_cpf
            else:
                self.creation_stats['duplicate_cpf_skips'] += 1
        
        raise ValueError(f"Could not generate unique CPF after {max_attempts} attempts")

    @transaction.atomic
    def generate_customers(self, count=100, temporary_ratio=0.7):
        """
        Generate a specified number of customers.
        
        Args:
            count (int): Number of customers to create
            temporary_ratio (float): Ratio of temporary to permanent accounts (0.0-1.0)
            
        Returns:
            list: List of created Customer objects
        """
        if self.verbose:
            print(f"Generating {count} customers ({temporary_ratio:.0%} temporary)...")
        
        customers = []
        
        for i in range(count):
            try:
                # Determine account type
                is_temporary = random.random() < temporary_ratio
                
                # Generate customer data
                name = generate_random_name()
                cpf = self._generate_unique_cpf()
                phone = self._generate_phone_number()
                address = self._generate_address()
                balance = self._generate_balance(is_temporary)
                
                # Create customer
                customer_data = {
                    'name': name,
                    'cpf': cpf,
                    'phone': phone,
                    'address': address,
                    'balance': balance,
                    'is_temporary': is_temporary,
                }
                
                # Add email for permanent accounts
                if not is_temporary:
                    customer_data['email'] = self._generate_email(name)
                
                customer = Cliente.objects.create(**customer_data)
                
                # Assign dietary restrictions
                restrictions_count = self._assign_dietary_restrictions(customer)
                
                customers.append(customer)
                self.created_customers.append(customer)
                
                # Update statistics
                self.creation_stats['total_customers'] += 1
                if is_temporary:
                    self.creation_stats['temporary_customers'] += 1
                else:
                    self.creation_stats['permanent_customers'] += 1
                
                if restrictions_count > 0:
                    self.creation_stats['customers_with_restrictions'] += 1
                    self.creation_stats['total_restrictions_assigned'] += restrictions_count
                
                if self.verbose and (i + 1) % 10 == 0:
                    print(f"  Created {i + 1}/{count} customers...")
                    
            except Exception as e:
                if self.verbose:
                    print(f"  Error creating customer {i + 1}: {str(e)}")
                continue
        
        if self.verbose:
            print(f"Successfully created {len(customers)} customers")
        
        return customers

    def generate_customer_batch(self, batch_size=50, **kwargs):
        """
        Generate customers in batches for better performance.
        
        Args:
            batch_size (int): Number of customers to create in each batch
            **kwargs: Additional arguments passed to generate_customers
            
        Returns:
            list: List of created Customer objects
        """
        total_count = kwargs.get('count', 100)
        all_customers = []
        
        for start in range(0, total_count, batch_size):
            end = min(start + batch_size, total_count)
            batch_count = end - start
            
            if self.verbose:
                print(f"Creating batch {start//batch_size + 1}: customers {start + 1}-{end}")
            
            batch_kwargs = kwargs.copy()
            batch_kwargs['count'] = batch_count
            
            batch_customers = self.generate_customers(**batch_kwargs)
            all_customers.extend(batch_customers)
        
        return all_customers

    def get_creation_summary(self):
        """
        Get a summary of the customer creation process.
        
        Returns:
            dict: Statistics about created customers
        """
        return self.creation_stats.copy()

    def clear_created_customers(self):
        """Clear the list of created customers and reset statistics."""
        self.created_customers.clear()
        self.creation_stats = {
            'total_customers': 0,
            'temporary_customers': 0,
            'permanent_customers': 0,
            'customers_with_restrictions': 0,
            'total_restrictions_assigned': 0,
            'cpf_generation_attempts': 0,
            'duplicate_cpf_skips': 0
        }

    def get_customers_by_type(self, is_temporary=True):
        """
        Get created customers filtered by account type.
        
        Args:
            is_temporary (bool): True for temporary accounts, False for permanent
            
        Returns:
            list: Filtered list of customers
        """
        return [c for c in self.created_customers if c.is_temporary == is_temporary]

    def get_customers_with_balance_range(self, min_balance=0, max_balance=None):
        """
        Get created customers within a specific balance range.
        
        Args:
            min_balance (float): Minimum balance
            max_balance (float): Maximum balance (None for no limit)
            
        Returns:
            list: Filtered list of customers
        """
        customers = []
        for customer in self.created_customers:
            if customer.balance >= min_balance:
                if max_balance is None or customer.balance <= max_balance:
                    customers.append(customer)
        return customers