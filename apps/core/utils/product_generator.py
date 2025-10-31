"""
Product data generator for creating realistic Brazilian fast food products.

This module generates diverse food items, beverages, and combo meals with
realistic pricing, nutritional information, and preparation times based on
authentic Brazilian fast food data.
"""

import random
from decimal import Decimal
from datetime import date, timedelta
from typing import List, Dict, Any, Optional

from django.db import transaction
from django.utils import timezone

from apps.produto.models import (
    Produto, Alimento, Bebida, Comida, Combo, ComboItem, RestricaoAlimentar
)
from apps.restaurante.models import Restaurante
from apps.core.utils.food_data import (
    FOOD_ITEMS, BEVERAGES, COMBO_TEMPLATES, DIETARY_RESTRICTIONS,
    get_all_food_items, get_random_food_item, get_random_beverage,
    get_beverages_by_category, get_random_combo_template,
    calculate_combo_price
)


class ProductDataGenerator:
    """
    Generates realistic product data for Brazilian fast food restaurants.
    
    Creates diverse food items, beverages, and combo meals with authentic
    Brazilian names, realistic pricing, nutritional information, and
    proper relationships between products and restaurants.
    """
    
    def __init__(self, verbose: bool = False):
        """
        Initialize the product data generator.
        
        Args:
            verbose (bool): Enable verbose output during generation
        """
        self.verbose = verbose
        self.creation_stats = {
            'food_items': 0,
            'beverages': 0,
            'combos': 0,
            'total_products': 0,
            'restaurant_associations': 0,
            'errors': 0
        }
        
        # Cache for created products to avoid duplicates
        self._created_products = {}
        self._dietary_restrictions_cache = {}
        
    def generate_products_for_restaurants(
        self, 
        restaurants: List[Restaurante], 
        products_per_restaurant: int = 50
    ) -> Dict[str, Any]:
        """
        Generate products and associate them with restaurants.
        
        Args:
            restaurants (List[Restaurante]): List of restaurants to create products for
            products_per_restaurant (int): Number of products to create per restaurant
            
        Returns:
            Dict[str, Any]: Generation statistics and created products
        """
        if self.verbose:
            print(f"Generating {products_per_restaurant} products for {len(restaurants)} restaurants...")
        
        try:
            with transaction.atomic():
                # First, create all unique products
                all_products = self._create_all_products(products_per_restaurant)
                
                # Then associate products with restaurants
                self._associate_products_with_restaurants(restaurants, all_products)
                
                if self.verbose:
                    self._print_generation_summary()
                
                return {
                    'products': all_products,
                    'stats': self.creation_stats.copy()
                }
                
        except Exception as e:
            self.creation_stats['errors'] += 1
            if self.verbose:
                print(f"Error during product generation: {str(e)}")
            raise
    
    def _create_all_products(self, target_count: int) -> List[Produto]:
        """
        Create all product types to reach the target count.
        
        Args:
            target_count (int): Target number of products to create
            
        Returns:
            List[Produto]: List of created products
        """
        all_products = []
        
        # Calculate distribution of product types
        food_count = int(target_count * 0.6)  # 60% food items
        beverage_count = int(target_count * 0.3)  # 30% beverages
        combo_count = target_count - food_count - beverage_count  # Remaining as combos
        
        if self.verbose:
            print(f"Creating {food_count} food items, {beverage_count} beverages, {combo_count} combos")
        
        # Create food items
        food_products = self._create_food_items(food_count)
        all_products.extend(food_products)
        
        # Create beverages
        beverage_products = self._create_beverages(beverage_count)
        all_products.extend(beverage_products)
        
        # Create combos (after food and beverages exist)
        combo_products = self._create_combos(combo_count, food_products + beverage_products)
        all_products.extend(combo_products)
        
        return all_products
    
    def _create_food_items(self, count: int) -> List[Produto]:
        """
        Create diverse food items based on Brazilian fast food data.
        
        Args:
            count (int): Number of food items to create
            
        Returns:
            List[Produto]: List of created food products
        """
        created_foods = []
        all_food_data = get_all_food_items()
        
        # Ensure we have dietary restrictions available
        self._ensure_dietary_restrictions()
        
        for i in range(count):
            try:
                # Select food data (cycle through available items with variations)
                base_food = all_food_data[i % len(all_food_data)]
                
                # Create variations for popular items
                variation_suffix = ""
                if i >= len(all_food_data):
                    variations = ["Especial", "Premium", "Light", "Duplo", "Grande"]
                    variation_suffix = f" {random.choice(variations)}"
                
                # Generate expiration date (1-7 days from now for fresh items)
                expiration_date = date.today() + timedelta(days=random.randint(1, 7))
                
                # Create the food item
                if base_food['category'] in ['Lanches', 'Acompanhamentos']:
                    # Create as Comida (solid food)
                    food_item = Comida.objects.create(
                        name=base_food['name'] + variation_suffix,
                        description=base_food['description'],
                        price=self._add_price_variation(base_food['base_price']),
                        category=base_food['category'],
                        expiration_date=expiration_date,
                        calories=base_food['calories'],
                        time_to_prepare=base_food['prep_time'],
                        weight_grams=random.randint(150, 500),
                        persons_served=random.randint(1, 2),
                        spice_level=random.choice(['suave', 'medio', 'picante']),
                        available=True
                    )
                else:
                    # Create as generic Alimento for other categories
                    food_item = Alimento.objects.create(
                        name=base_food['name'] + variation_suffix,
                        description=base_food['description'],
                        price=self._add_price_variation(base_food['base_price']),
                        category=base_food['category'],
                        expiration_date=expiration_date,
                        calories=base_food['calories'],
                        time_to_prepare=base_food['prep_time'],
                        weight_grams=random.randint(100, 800),
                        available=True
                    )
                
                # Add dietary restrictions
                self._add_dietary_restrictions(food_item)
                
                created_foods.append(food_item)
                self.creation_stats['food_items'] += 1
                
                if self.verbose and (i + 1) % 10 == 0:
                    print(f"  Created {i + 1}/{count} food items")
                    
            except Exception as e:
                self.creation_stats['errors'] += 1
                if self.verbose:
                    print(f"  Error creating food item {i + 1}: {str(e)}")
                continue
        
        return created_foods
    
    def _create_beverages(self, count: int) -> List[Produto]:
        """
        Create diverse beverages with various sizes and temperature options.
        
        Args:
            count (int): Number of beverages to create
            
        Returns:
            List[Produto]: List of created beverage products
        """
        created_beverages = []
        
        for i in range(count):
            try:
                # Select beverage data
                base_beverage = BEVERAGES[i % len(BEVERAGES)]
                
                # Select a random size
                size_name, size_data = random.choice(list(base_beverage['sizes'].items()))
                
                # Generate expiration date (longer for beverages)
                expiration_date = date.today() + timedelta(days=random.randint(30, 180))
                
                # Extract volume from size name (e.g., "Médio (500ml)" -> 500)
                volume_ml = int(size_name.split('(')[1].split('ml')[0])
                
                # Create variation name
                variation_name = f"{base_beverage['name']} {size_name.split(' (')[0]}"
                
                # Create the beverage
                beverage = Bebida.objects.create(
                    name=variation_name,
                    description=f"{base_beverage['description']} - {size_name}",
                    price=size_data['price'],
                    category=base_beverage['category'],
                    expiration_date=expiration_date,
                    calories=size_data['calories'],
                    time_to_prepare=base_beverage['prep_time'],
                    weight_grams=volume_ml,  # Use volume as weight for beverages
                    volume_ml=volume_ml,
                    is_alcoholic=False,  # Fast food restaurants typically don't serve alcohol
                    temperature=self._get_beverage_temperature(base_beverage['category']),
                    available=True
                )
                
                # Add dietary restrictions for beverages
                self._add_dietary_restrictions(beverage, is_beverage=True)
                
                created_beverages.append(beverage)
                self.creation_stats['beverages'] += 1
                
                if self.verbose and (i + 1) % 5 == 0:
                    print(f"  Created {i + 1}/{count} beverages")
                    
            except Exception as e:
                self.creation_stats['errors'] += 1
                if self.verbose:
                    print(f"  Error creating beverage {i + 1}: {str(e)}")
                continue
        
        return created_beverages
    
    def _create_combos(self, count: int, available_products: List[Produto]) -> List[Produto]:
        """
        Create combo meals with item associations and discounts.
        
        Args:
            count (int): Number of combos to create
            available_products (List[Produto]): Products available for combo creation
            
        Returns:
            List[Produto]: List of created combo products
        """
        created_combos = []
        
        if len(available_products) < 3:
            if self.verbose:
                print("  Not enough products to create combos, skipping combo creation")
            return created_combos
        
        for i in range(count):
            try:
                # Select combo template
                combo_template = COMBO_TEMPLATES[i % len(COMBO_TEMPLATES)]
                
                # Create variation name
                variation_suffix = ""
                if i >= len(COMBO_TEMPLATES):
                    variations = ["Especial", "Premium", "Família", "Econômico"]
                    variation_suffix = f" {random.choice(variations)}"
                
                # Create the combo
                combo = Combo.objects.create(
                    name=combo_template['name'] + variation_suffix,
                    description=combo_template['description'],
                    price=Decimal('0.00'),  # Will be calculated after adding items
                    category=combo_template['category'],
                    discount_percentage=Decimal(str(combo_template['discount_percent'])),
                    available=True
                )
                
                # Add items to combo
                combo_items = self._select_combo_items(combo_template, available_products)
                total_price = Decimal('0.00')
                
                for product, quantity in combo_items:
                    ComboItem.objects.create(
                        combo=combo,
                        produto=product,
                        quantity=quantity
                    )
                    total_price += product.price * quantity
                
                # Calculate final price with discount
                discount_amount = total_price * (combo.discount_percentage / 100)
                final_price = total_price - discount_amount
                
                combo.price = final_price
                combo.save()
                
                created_combos.append(combo)
                self.creation_stats['combos'] += 1
                
                if self.verbose:
                    print(f"  Created combo: {combo.name} (R$ {final_price:.2f})")
                    
            except Exception as e:
                self.creation_stats['errors'] += 1
                if self.verbose:
                    print(f"  Error creating combo {i + 1}: {str(e)}")
                continue
        
        return created_combos
    
    def _associate_products_with_restaurants(
        self, 
        restaurants: List[Restaurante], 
        products: List[Produto]
    ) -> None:
        """
        Associate products with restaurant menus ensuring availability and pricing consistency.
        
        Args:
            restaurants (List[Restaurante]): Restaurants to associate products with
            products (List[Produto]): Products to associate
        """
        if self.verbose:
            print(f"Associating {len(products)} products with {len(restaurants)} restaurants...")
        
        # Ensure all products are available before association
        available_products = [p for p in products if p.available]
        
        for restaurant in restaurants:
            # Each restaurant gets most products, but with some variation
            # Ensure core items (popular categories) are always included
            core_products = [p for p in available_products 
                           if hasattr(p, 'category') and p.category in ['Lanches', 'Bebidas']]
            
            # Add all core products
            restaurant_products = core_products.copy()
            
            # Add random selection of remaining products
            remaining_products = [p for p in available_products if p not in core_products]
            if remaining_products:
                additional_count = random.randint(
                    int(len(remaining_products) * 0.5), 
                    len(remaining_products)
                )
                additional_products = random.sample(remaining_products, 
                                                  min(additional_count, len(remaining_products)))
                restaurant_products.extend(additional_products)
            
            # Associate products with restaurant menu
            for product in restaurant_products:
                # Ensure product is available and has valid pricing
                if product.available and product.price > 0:
                    restaurant.menu.add(product)
                    self.creation_stats['restaurant_associations'] += 1
            
            if self.verbose:
                print(f"  {restaurant.name}: {len(restaurant_products)} products added to menu")
                
        # Verify pricing consistency across restaurants
        self._verify_pricing_consistency(restaurants)
    
    def _select_combo_items(
        self, 
        combo_template: Dict[str, Any], 
        available_products: List[Produto]
    ) -> List[tuple]:
        """
        Select appropriate items for a combo based on the template.
        
        Args:
            combo_template (Dict[str, Any]): Combo template with item requirements
            available_products (List[Produto]): Available products to choose from
            
        Returns:
            List[tuple]: List of (product, quantity) tuples
        """
        combo_items = []
        
        # Select main items
        main_items = [p for p in available_products 
                     if hasattr(p, 'alimento') and p.category in ['Lanches', 'Pizzas']]
        if main_items:
            main_item = random.choice(main_items)
            combo_items.append((main_item, 1))
        
        # Select side items
        side_items = [p for p in available_products 
                     if hasattr(p, 'alimento') and p.category == 'Acompanhamentos']
        if side_items:
            side_item = random.choice(side_items)
            combo_items.append((side_item, 1))
        
        # Select beverages
        beverages = [p for p in available_products 
                    if hasattr(p, 'bebida')]
        if beverages:
            beverage = random.choice(beverages)
            quantity = combo_template.get('drink_quantity', 1)
            combo_items.append((beverage, quantity))
        
        # Add dessert if specified in template
        if 'dessert_items' in combo_template:
            desserts = [p for p in available_products 
                       if hasattr(p, 'alimento') and p.category == 'Sobremesas']
            if desserts:
                dessert = random.choice(desserts)
                combo_items.append((dessert, 1))
        
        return combo_items
    
    def _add_price_variation(self, base_price: Decimal) -> Decimal:
        """
        Add realistic price variation to base prices.
        
        Args:
            base_price (Decimal): Base price from data
            
        Returns:
            Decimal: Price with variation applied
        """
        # Add ±20% variation
        variation = random.uniform(-0.2, 0.2)
        new_price = base_price * (1 + Decimal(str(variation)))
        
        # Round to nearest 0.10
        return (new_price * 10).quantize(Decimal('1')) / 10
    
    def _get_beverage_temperature(self, category: str) -> str:
        """
        Get appropriate temperature for beverage category.
        
        Args:
            category (str): Beverage category
            
        Returns:
            str: Temperature choice
        """
        temperature_map = {
            'Refrigerantes': 'gelada',
            'Sucos Naturais': 'gelada',
            'Águas': 'natural',
            'Cafés': 'quente',
            'Milkshakes': 'gelada'
        }
        return temperature_map.get(category, 'natural')
    
    def _ensure_dietary_restrictions(self) -> None:
        """Ensure dietary restrictions exist in the database."""
        if self._dietary_restrictions_cache:
            return
        
        for restriction_data in DIETARY_RESTRICTIONS:
            restriction, created = RestricaoAlimentar.objects.get_or_create(
                name=restriction_data['name'],
                defaults={'description': restriction_data['description']}
            )
            self._dietary_restrictions_cache[restriction.name] = restriction
    
    def _add_dietary_restrictions(self, product: Alimento, is_beverage: bool = False) -> None:
        """
        Add appropriate dietary restrictions to a product.
        
        Args:
            product (Alimento): Product to add restrictions to
            is_beverage (bool): Whether the product is a beverage
        """
        # Randomly assign some dietary restrictions
        possible_restrictions = []
        
        if is_beverage:
            # Beverages typically have fewer restrictions
            if 'Açúcar' not in product.name and 'Diet' not in product.name:
                if random.random() < 0.1:  # 10% chance
                    possible_restrictions.append('Sem Açúcar')
        else:
            # Food items can have various restrictions
            if random.random() < 0.3:  # 30% chance of having gluten
                possible_restrictions.append('Glúten')
            
            if random.random() < 0.4:  # 40% chance of having lactose
                possible_restrictions.append('Lactose')
            
            if random.random() < 0.05:  # 5% chance of being vegan
                possible_restrictions.append('Vegano')
            elif random.random() < 0.1:  # 10% chance of being vegetarian
                possible_restrictions.append('Vegetariano')
            
            if product.calories > 400 and random.random() < 0.2:  # 20% chance for high-calorie items
                possible_restrictions.append('Fonte de Proteína')
        
        # Add selected restrictions
        for restriction_name in possible_restrictions:
            if restriction_name in self._dietary_restrictions_cache:
                product.alimentary_restrictions.add(
                    self._dietary_restrictions_cache[restriction_name]
                )
    
    def _print_generation_summary(self) -> None:
        """Print a summary of the generation process."""
        print("\n=== Product Generation Summary ===")
        print(f"Food items created: {self.creation_stats['food_items']}")
        print(f"Beverages created: {self.creation_stats['beverages']}")
        print(f"Combos created: {self.creation_stats['combos']}")
        print(f"Total products: {sum([self.creation_stats['food_items'], self.creation_stats['beverages'], self.creation_stats['combos']])}")
        print(f"Restaurant associations: {self.creation_stats['restaurant_associations']}")
        if self.creation_stats['errors'] > 0:
            print(f"Errors encountered: {self.creation_stats['errors']}")
        print("=" * 35)
    
    def _verify_pricing_consistency(self, restaurants: List[Restaurante]) -> None:
        """
        Verify that product pricing is consistent across restaurants.
        
        Args:
            restaurants (List[Restaurante]): Restaurants to verify
        """
        if self.verbose:
            print("Verifying pricing consistency across restaurants...")
        
        # Get all unique products across all restaurants
        all_menu_products = set()
        for restaurant in restaurants:
            all_menu_products.update(restaurant.menu.all())
        
        # Check for any pricing inconsistencies (shouldn't happen with our implementation)
        pricing_issues = 0
        availability_issues = 0
        
        for product in all_menu_products:
            # Check availability
            if not product.available:
                availability_issues += 1
                if self.verbose:
                    print(f"  Warning: Unavailable product in menu: {product.name}")
            
            # Check pricing
            if product.price <= 0:
                pricing_issues += 1
                if self.verbose:
                    print(f"  Warning: Invalid price for product: {product.name} (R$ {product.price})")
        
        if self.verbose:
            if pricing_issues == 0 and availability_issues == 0:
                print("  ✓ All products have consistent pricing and availability")
            else:
                print(f"  Found {pricing_issues} pricing issues and {availability_issues} availability issues")
    
    def get_creation_summary(self) -> Dict[str, int]:
        """
        Get summary of creation statistics.
        
        Returns:
            Dict[str, int]: Creation statistics
        """
        self.creation_stats['total_products'] = (
            self.creation_stats['food_items'] + 
            self.creation_stats['beverages'] + 
            self.creation_stats['combos']
        )
        return self.creation_stats.copy()