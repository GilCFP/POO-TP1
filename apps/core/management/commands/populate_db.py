"""
Django management command to populate the database with realistic test data.

This command generates comprehensive test data including:
- Restaurants with kitchens and cashier systems
- Products (food items, beverages, combos) with realistic pricing
- Customers with valid Brazilian CPF numbers and names
- Historical orders with realistic patterns and status progressions

Usage:
    python manage.py populate_db
    python manage.py populate_db --restaurants 3 --products 100 --customers 200 --orders 500
    python manage.py populate_db --clear-existing
    python manage.py populate_db --minimal
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
import logging

from apps.core.utils.restaurant_generator import RestaurantDataGenerator
from apps.core.utils.category_setup import setup_categories_and_restrictions
from apps.core.utils.product_generator import ProductDataGenerator
from apps.core.utils.customer_generator import CustomerDataGenerator
from apps.core.utils.order_generator import OrderDataGenerator
from apps.core.utils.data_validator import DataValidator
from apps.core.utils.duplicate_prevention import DuplicatePreventionManager
from apps.pedido.models import StatusPedido

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Django management command for populating the database with realistic test data.
    
    This command creates interconnected data across all models with realistic
    Brazilian names, valid CPF numbers, authentic food items, and historical
    order patterns that simulate real business operations.
    """
    
    help = (
        'Populates database with realistic test data for fast food restaurant application. '
        'Creates restaurants, products, customers, and orders with authentic Brazilian data.'
    )

    def add_arguments(self, parser):
        """
        Add command-line arguments for controlling data generation behavior.
        
        Arguments control data volume, clearing existing data, and generation modes.
        """
        # Data volume control arguments
        parser.add_argument(
            '--restaurants',
            type=int,
            default=2,
            help='Number of restaurants to create (default: 2)'
        )
        
        parser.add_argument(
            '--products',
            type=int,
            default=50,
            help='Number of products to create per restaurant (default: 50)'
        )
        
        parser.add_argument(
            '--customers',
            type=int,
            default=100,
            help='Number of customers to create (default: 100)'
        )
        
        parser.add_argument(
            '--orders',
            type=int,
            default=200,
            help='Number of historical orders to create (default: 200)'
        )
        
        # Data management arguments
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Clear all existing data before populating (WARNING: This will delete all data!)'
        )
        
        parser.add_argument(
            '--append',
            action='store_true',
            help='Append to existing data instead of checking for duplicates'
        )
        
        # Preset configurations
        parser.add_argument(
            '--minimal',
            action='store_true',
            help='Create minimal test dataset (1 restaurant, 20 products, 25 customers, 50 orders)'
        )
        
        parser.add_argument(
            '--full',
            action='store_true',
            help='Create comprehensive test dataset (5 restaurants, 100 products, 500 customers, 1000 orders)'
        )
        
        # Behavior control arguments
        parser.add_argument(
            '--no-progress',
            action='store_true',
            help='Disable progress reporting during data generation'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without actually creating data'
        )
        
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose output with detailed creation information'
        )
        
        # Data validation arguments
        parser.add_argument(
            '--skip-validation',
            action='store_true',
            help='Skip data validation checks (not recommended)'
        )
        
        parser.add_argument(
            '--validate-relationships',
            action='store_true',
            help='Validate data relationships after population'
        )

    def handle(self, *args, **options):
        """
        Main command execution logic.
        
        Orchestrates the data generation process in the correct dependency order:
        1. Validate arguments and database connection
        2. Initialize validation and duplicate prevention
        3. Handle existing data (clear or check for duplicates)
        4. Create foundation data (restaurants, dietary restrictions)
        5. Generate product catalog
        6. Create customer base
        7. Generate order history
        8. Validate data relationships
        9. Display summary report
        """
        try:
            # Apply preset configurations
            self._apply_presets(options)
            
            # Validate arguments
            self._validate_arguments(options)
            
            # Initialize validation and duplicate prevention
            self.validator = DataValidator(verbose=options['verbose'])
            self.duplicate_manager = DuplicatePreventionManager(
                verbose=options['verbose'],
                append_mode=options['append']
            )
            
            # Display configuration summary
            self._display_configuration(options)
            
            if options['dry_run']:
                self.stdout.write(
                    self.style.WARNING('DRY RUN MODE: No data will be created')
                )
                return
            
            # Check existing data and validate relationships
            if not options['skip_validation']:
                self._validate_existing_data(options)
            
            # Confirm destructive operations
            if options['clear_existing']:
                if not self._confirm_clear_data():
                    self.stdout.write(
                        self.style.WARNING('Operation cancelled by user')
                    )
                    return
                
                # Clear existing data
                self.duplicate_manager.clear_all_data(confirm=True)
            
            # Execute data population with transaction management
            with transaction.atomic():
                self._populate_database(options)
                
                # Validate relationships after population
                if options['validate_relationships'] and not options['skip_validation']:
                    self._validate_final_relationships()
                
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.ERROR('\nOperation cancelled by user')
            )
        except Exception as e:
            logger.exception("Error during database population")
            raise CommandError(f'Database population failed: {str(e)}')

    def _apply_presets(self, options):
        """Apply preset configurations for minimal or full data sets."""
        if options['minimal']:
            options.update({
                'restaurants': 1,
                'products': 20,
                'customers': 25,
                'orders': 50
            })
            self.stdout.write(
                self.style.SUCCESS('Applied minimal dataset configuration')
            )
        elif options['full']:
            options.update({
                'restaurants': 5,
                'products': 100,
                'customers': 500,
                'orders': 1000
            })
            self.stdout.write(
                self.style.SUCCESS('Applied full dataset configuration')
            )

    def _validate_arguments(self, options):
        """Validate command-line arguments for consistency and safety."""
        # Validate positive numbers
        for key in ['restaurants', 'products', 'customers', 'orders']:
            if options[key] < 0:
                raise CommandError(f'{key} must be a positive number')
        
        # Validate mutually exclusive options
        if options['clear_existing'] and options['append']:
            raise CommandError(
                '--clear-existing and --append are mutually exclusive'
            )
        
        if options['minimal'] and options['full']:
            raise CommandError(
                '--minimal and --full are mutually exclusive'
            )
        
        # Warn about large data sets
        total_items = (
            options['restaurants'] + options['products'] + 
            options['customers'] + options['orders']
        )
        if total_items > 5000:
            self.stdout.write(
                self.style.WARNING(
                    f'Large dataset requested ({total_items} total items). '
                    'This may take several minutes to complete.'
                )
            )

    def _display_configuration(self, options):
        """Display the current configuration before execution."""
        self.stdout.write(
            self.style.HTTP_INFO('\n=== Database Population Configuration ===')
        )
        self.stdout.write(f"Restaurants: {options['restaurants']}")
        self.stdout.write(f"Products: {options['products']}")
        self.stdout.write(f"Customers: {options['customers']}")
        self.stdout.write(f"Orders: {options['orders']}")
        
        if options['clear_existing']:
            self.stdout.write(
                self.style.WARNING('Mode: Clear existing data')
            )
        elif options['append']:
            self.stdout.write('Mode: Append to existing data')
        else:
            self.stdout.write('Mode: Skip duplicates')
        
        self.stdout.write('=' * 45 + '\n')

    def _confirm_clear_data(self):
        """Confirm destructive clear operation with user."""
        self.stdout.write(
            self.style.ERROR(
                'WARNING: This will permanently delete ALL existing data!'
            )
        )
        self.stdout.write('This includes:')
        self.stdout.write('- All restaurants and their configurations')
        self.stdout.write('- All products, food items, and combos')
        self.stdout.write('- All customer accounts and profiles')
        self.stdout.write('- All orders and order history')
        self.stdout.write('- All related data and relationships')
        
        response = input('\nAre you sure you want to continue? (yes/no): ')
        return response.lower() in ['yes', 'y']

    def _populate_database(self, options):
        """
        Execute the main data population process.
        
        This method orchestrates the creation of all test data in the proper
        dependency order: restaurants → products → customers → orders.
        """
        self.stdout.write(
            self.style.SUCCESS('Starting database population...')
        )
        
        # Progress tracking
        progress_enabled = not options['no_progress']
        verbose = options['verbose']
        
        # Data generation statistics
        stats = {
            'restaurants': 0,
            'kitchens': 0,
            'cashiers': 0,
            'dietary_restrictions': 0,
            'products': 0,
            'customers': 0,
            'orders': 0,
            'order_items': 0,
            'status_history_records': 0,
            'errors': 0
        }
        
        try:
            # 1. Create restaurants and infrastructure
            if progress_enabled:
                self.stdout.write('Creating restaurants and infrastructure...')
            
            restaurant_stats, restaurants = self._create_restaurants(options, verbose)
            stats.update(restaurant_stats)
            
            # 2. Generate product catalog
            if progress_enabled:
                self.stdout.write('Creating product catalog...')
            
            product_stats = self._create_products(options, verbose, restaurants)
            stats.update(product_stats)
            
            # 3. Create customer base
            if progress_enabled:
                self.stdout.write('Creating customer base...')
            
            customer_stats = self._create_customers(options, verbose)
            stats.update(customer_stats)
            
            # 4. Generate order history
            if progress_enabled:
                self.stdout.write('Creating order history...')
            
            order_stats = self._create_orders(options, verbose)
            stats.update(order_stats)
            
            # Display final summary
            self._display_summary(stats, options)
            
        except Exception as e:
            stats['errors'] += 1
            logger.exception("Error during data population")
            raise CommandError(f'Data population failed: {str(e)}')

    def _create_restaurants(self, options, verbose):
        """
        Create restaurants and infrastructure using RestaurantDataGenerator.
        
        Args:
            options (dict): Command options
            verbose (bool): Enable verbose output
            
        Returns:
            tuple: (dict of statistics, list of restaurant objects)
        """
        # Set up categories and dietary restrictions first
        setup, category_summary = setup_categories_and_restrictions(verbose=verbose)
        
        # Create restaurant generator
        generator = RestaurantDataGenerator(verbose=verbose)
        
        # Generate restaurants with validation and duplicate prevention
        restaurants_data = generator.generate_restaurants(
            count=options['restaurants'],
            validator=getattr(self, 'validator', None),
            duplicate_manager=getattr(self, 'duplicate_manager', None)
        )
        
        # Extract restaurant objects from the data
        restaurants = [data['restaurant'] for data in restaurants_data]
        
        # Get creation summary
        creation_summary = generator.get_creation_summary()
        
        # Combine summaries
        stats = {
            'restaurants': creation_summary['restaurants'],
            'kitchens': creation_summary['kitchens'],
            'cashiers': creation_summary['cashiers'],
            'dietary_restrictions': category_summary['restrictions_created'],
            'total_stations': creation_summary['total_stations']
        }
        
        if verbose or not options.get('no_progress', False):
            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ Created {stats['restaurants']} restaurants with "
                    f"{stats['kitchens']} kitchens and {stats['cashiers']} cashier systems"
                )
            )
            self.stdout.write(
                f"  Total work stations: {stats['total_stations']}"
            )
            self.stdout.write(
                f"  Dietary restrictions: {stats['dietary_restrictions']} created"
            )
        
        return stats, restaurants

    def _create_products(self, options, verbose, restaurants):
        """
        Create products using ProductDataGenerator.
        
        Args:
            options (dict): Command options
            verbose (bool): Enable verbose output
            restaurants (list): List of created restaurants
            
        Returns:
            dict: Statistics of created products
        """
        # Create product generator
        generator = ProductDataGenerator(verbose=verbose)
        
        # Generate products for all restaurants
        result = generator.generate_products_for_restaurants(
            restaurants=restaurants,
            products_per_restaurant=options['products']
        )
        
        # Get creation summary
        creation_summary = generator.get_creation_summary()
        
        if verbose or not options.get('no_progress', False):
            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ Created {creation_summary['total_products']} products "
                    f"({creation_summary['food_items']} food items, "
                    f"{creation_summary['beverages']} beverages, "
                    f"{creation_summary['combos']} combos)"
                )
            )
            self.stdout.write(
                f"  Restaurant menu associations: {creation_summary['restaurant_associations']}"
            )
        
        return creation_summary

    def _create_customers(self, options, verbose):
        """
        Create customers using CustomerDataGenerator.
        
        Args:
            options (dict): Command options
            verbose (bool): Enable verbose output
            
        Returns:
            dict: Statistics of created customers
        """
        # Create customer generator
        generator = CustomerDataGenerator(verbose=verbose)
        
        # Generate customers with 70% temporary, 30% permanent ratio
        customers = generator.generate_customers(
            count=options['customers'],
            temporary_ratio=0.7
        )
        
        # Get creation summary
        creation_summary = generator.get_creation_summary()
        
        if verbose or not options.get('no_progress', False):
            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ Created {creation_summary['total_customers']} customers "
                    f"({creation_summary['temporary_customers']} temporary, "
                    f"{creation_summary['permanent_customers']} permanent)"
                )
            )
            self.stdout.write(
                f"  Customers with dietary restrictions: {creation_summary['customers_with_restrictions']}"
            )
            self.stdout.write(
                f"  Total dietary restrictions assigned: {creation_summary['total_restrictions_assigned']}"
            )
            if creation_summary['duplicate_cpf_skips'] > 0:
                self.stdout.write(
                    f"  CPF generation attempts: {creation_summary['cpf_generation_attempts']} "
                    f"(skipped {creation_summary['duplicate_cpf_skips']} duplicates)"
                )
        
        return creation_summary

    def _create_orders(self, options, verbose):
        """
        Create orders using OrderDataGenerator.
        
        Args:
            options (dict): Command options
            verbose (bool): Enable verbose output
            
        Returns:
            dict: Statistics of created orders
        """
        # Create order generator
        generator = OrderDataGenerator(verbose=verbose)
        
        # Generate orders with 30-day history
        orders = generator.generate_orders(
            count=options['orders'],
            days_back=30
        )
        
        # Get creation summary
        creation_summary = generator.get_creation_summary()
        
        if verbose or not options.get('no_progress', False):
            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ Created {creation_summary['total_orders']} orders "
                    f"with {creation_summary['total_order_items']} items"
                )
            )
            self.stdout.write(
                f"  Total order value: R$ {creation_summary['total_order_value']:.2f}"
            )
            self.stdout.write(
                f"  Average order value: R$ {creation_summary['average_order_value']:.2f}"
            )
            self.stdout.write(
                f"  Orders with special instructions: {creation_summary['orders_with_special_instructions']}"
            )
            self.stdout.write(
                f"  Status history records: {creation_summary['status_history_records']}"
            )
            
            # Display status distribution
            if creation_summary['orders_by_status']:
                self.stdout.write("  Order status distribution:")
                for status, count in creation_summary['orders_by_status'].items():
                    status_display = dict(StatusPedido.choices).get(status, status)
                    percentage = (count / creation_summary['total_orders']) * 100
                    self.stdout.write(f"    {status_display}: {count} ({percentage:.1f}%)")
        
        # Map summary keys to match stats structure
        return {
            'orders': creation_summary['total_orders'],
            'order_items': creation_summary['total_order_items'],
            'status_history_records': creation_summary['status_history_records'],
            'total_order_value': creation_summary['total_order_value'],
            'average_order_value': creation_summary['average_order_value'],
            'orders_with_special_instructions': creation_summary['orders_with_special_instructions'],
            'orders_by_status': creation_summary['orders_by_status'],
            'orders_by_payment_method': creation_summary['orders_by_payment_method'],
            'orders_by_time_period': creation_summary['orders_by_time_period']
        }

    def _display_summary(self, stats, options):
        """Display summary of created data."""
        self.stdout.write(
            self.style.HTTP_INFO('\n=== Population Summary ===')
        )
        self.stdout.write(f"Restaurants created: {stats.get('restaurants', 0)}")
        self.stdout.write(f"Kitchens created: {stats.get('kitchens', 0)}")
        self.stdout.write(f"Cashier systems created: {stats.get('cashiers', 0)}")
        self.stdout.write(f"Work stations created: {stats.get('total_stations', 0)}")
        self.stdout.write(f"Dietary restrictions created: {stats.get('dietary_restrictions', 0)}")
        self.stdout.write(f"Products created: {stats.get('total_products', 0)}")
        self.stdout.write(f"  - Food items: {stats.get('food_items', 0)}")
        self.stdout.write(f"  - Beverages: {stats.get('beverages', 0)}")
        self.stdout.write(f"  - Combos: {stats.get('combos', 0)}")
        self.stdout.write(f"Restaurant menu associations: {stats.get('restaurant_associations', 0)}")
        self.stdout.write(f"Customers created: {stats.get('total_customers', 0)}")
        self.stdout.write(f"  - Temporary accounts: {stats.get('temporary_customers', 0)}")
        self.stdout.write(f"  - Permanent accounts: {stats.get('permanent_customers', 0)}")
        self.stdout.write(f"  - With dietary restrictions: {stats.get('customers_with_restrictions', 0)}")
        self.stdout.write(f"Orders created: {stats.get('orders', 0)}")
        self.stdout.write(f"  - Order items: {stats.get('order_items', 0)}")
        self.stdout.write(f"  - Status history records: {stats.get('status_history_records', 0)}")
        self.stdout.write(f"  - Total order value: R$ {stats.get('total_order_value', 0):.2f}")
        self.stdout.write(f"  - Average order value: R$ {stats.get('average_order_value', 0):.2f}")
        self.stdout.write(f"  - With special instructions: {stats.get('orders_with_special_instructions', 0)}")
        
        if stats.get('errors', 0) > 0:
            self.stdout.write(
                self.style.ERROR(f"Errors encountered: {stats['errors']}")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('Database population completed successfully!')
            )
        
        self.stdout.write('=' * 35)
        
        # Display validation and duplicate prevention summary
        self._display_validation_summary(stats, options)

    def _validate_existing_data(self, options):
        """Validate existing data and check for potential issues."""
        if options['verbose']:
            self.stdout.write('Validating existing data...')
        
        # Check existing data counts
        existing_counts = self.validator.check_existing_data(
            clear_existing=options['clear_existing']
        )
        
        # Validate relationships if data exists
        if any(existing_counts.values()) and not options['clear_existing']:
            if not self.validator.validate_data_relationships():
                validation_summary = self.validator.get_validation_summary()
                if validation_summary['has_errors']:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Found {validation_summary['error_count']} data relationship errors"
                        )
                    )
                    for error in validation_summary['errors']:
                        self.stdout.write(f"  - {error}")
                    
                    if not options['skip_validation']:
                        raise CommandError(
                            "Data validation failed. Use --skip-validation to proceed anyway."
                        )
                
                if validation_summary['has_warnings']:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Found {validation_summary['warning_count']} data warnings"
                        )
                    )
                    for warning in validation_summary['warnings']:
                        self.stdout.write(f"  - {warning}")
    
    def _validate_final_relationships(self):
        """Validate data relationships after population."""
        if hasattr(self, 'validator'):
            self.stdout.write('Validating final data relationships...')
            
            if self.validator.validate_data_relationships():
                self.stdout.write(
                    self.style.SUCCESS('✓ All data relationships are valid')
                )
            else:
                validation_summary = self.validator.get_validation_summary()
                if validation_summary['has_errors']:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Found {validation_summary['error_count']} relationship errors"
                        )
                    )
                    for error in validation_summary['errors']:
                        self.stdout.write(f"  - {error}")
                
                if validation_summary['has_warnings']:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Found {validation_summary['warning_count']} relationship warnings"
                        )
                    )
                    for warning in validation_summary['warnings']:
                        self.stdout.write(f"  - {warning}")
    
    def _display_validation_summary(self, stats, options):
        """Display validation and duplicate prevention summary."""
        if hasattr(self, 'validator'):
            validation_summary = self.validator.get_validation_summary()
            if validation_summary['has_errors'] or validation_summary['has_warnings']:
                self.stdout.write(
                    self.style.HTTP_INFO('\n=== Validation Summary ===')
                )
                if validation_summary['has_errors']:
                    self.stdout.write(f"Validation errors: {validation_summary['error_count']}")
                if validation_summary['has_warnings']:
                    self.stdout.write(f"Validation warnings: {validation_summary['warning_count']}")
        
        if hasattr(self, 'duplicate_manager'):
            duplicate_stats = self.duplicate_manager.get_duplicate_stats()
            if duplicate_stats['total_skipped'] > 0:
                self.stdout.write(
                    self.style.HTTP_INFO('\n=== Duplicate Prevention Summary ===')
                )
                self.stdout.write(f"Total duplicates skipped: {duplicate_stats['total_skipped']}")
                if duplicate_stats['restaurants_skipped'] > 0:
                    self.stdout.write(f"  Restaurants: {duplicate_stats['restaurants_skipped']}")
                if duplicate_stats['products_skipped'] > 0:
                    self.stdout.write(f"  Products: {duplicate_stats['products_skipped']}")
                if duplicate_stats['customers_skipped'] > 0:
                    self.stdout.write(f"  Customers: {duplicate_stats['customers_skipped']}")
                if duplicate_stats['orders_skipped'] > 0:
                    self.stdout.write(f"  Orders: {duplicate_stats['orders_skipped']}")
                if duplicate_stats['dietary_restrictions_skipped'] > 0:
                    self.stdout.write(f"  Dietary restrictions: {duplicate_stats['dietary_restrictions_skipped']}")
                self.stdout.write('=' * 40)