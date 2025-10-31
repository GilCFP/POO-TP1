"""
Product category setup utilities for organizing menu items.

This module provides utilities for setting up product categories that will be used
to organize menu items in a logical structure for fast food restaurants.
"""

from apps.produto.models import RestricaoAlimentar


class CategorySetup:
    """
    Utility class for setting up product categories and dietary restrictions.
    
    Provides methods to create and organize product categories that will be used
    by the ProductDataGenerator to properly categorize menu items.
    """
    
    # Standard fast food categories
    PRODUCT_CATEGORIES = [
        {
            'name': 'Lanches',
            'description': 'Hambúrgueres, sanduíches e lanches diversos',
            'display_order': 1,
            'icon': 'burger'
        },
        {
            'name': 'Pizzas',
            'description': 'Pizzas tradicionais e especiais',
            'display_order': 2,
            'icon': 'pizza'
        },
        {
            'name': 'Acompanhamentos',
            'description': 'Batatas fritas, nuggets e acompanhamentos',
            'display_order': 3,
            'icon': 'fries'
        },
        {
            'name': 'Bebidas',
            'description': 'Refrigerantes, sucos, águas e bebidas quentes',
            'display_order': 4,
            'icon': 'drink'
        },
        {
            'name': 'Sobremesas',
            'description': 'Sorvetes, tortas e doces',
            'display_order': 5,
            'icon': 'dessert'
        },
        {
            'name': 'Combos',
            'description': 'Combinações de produtos com desconto',
            'display_order': 6,
            'icon': 'combo'
        }
    ]
    
    # Dietary restrictions with detailed information
    DIETARY_RESTRICTIONS = [
        {
            'name': 'Glúten',
            'description': 'Contém glúten - não recomendado para celíacos',
            'icon': 'gluten',
            'color': '#ff6b6b',
            'is_allergen': True
        },
        {
            'name': 'Lactose',
            'description': 'Contém lactose - não recomendado para intolerantes',
            'icon': 'milk',
            'color': '#4ecdc4',
            'is_allergen': True
        },
        {
            'name': 'Vegano',
            'description': 'Produto 100% vegano - sem ingredientes de origem animal',
            'icon': 'leaf',
            'color': '#45b7d1',
            'is_allergen': False
        },
        {
            'name': 'Vegetariano',
            'description': 'Produto vegetariano - pode conter ovos e laticínios',
            'icon': 'vegetarian',
            'color': '#96ceb4',
            'is_allergen': False
        },
        {
            'name': 'Sem Açúcar',
            'description': 'Produto sem açúcar adicionado',
            'icon': 'no-sugar',
            'color': '#feca57',
            'is_allergen': False
        },
        {
            'name': 'Sem Gordura Trans',
            'description': 'Produto livre de gordura trans',
            'icon': 'no-trans-fat',
            'color': '#ff9ff3',
            'is_allergen': False
        },
        {
            'name': 'Rico em Fibras',
            'description': 'Produto com alto teor de fibras',
            'icon': 'fiber',
            'color': '#54a0ff',
            'is_allergen': False
        },
        {
            'name': 'Fonte de Proteína',
            'description': 'Produto com alto teor de proteína',
            'icon': 'protein',
            'color': '#5f27cd',
            'is_allergen': False
        },
        {
            'name': 'Sem Conservantes',
            'description': 'Produto sem conservantes artificiais',
            'icon': 'natural',
            'color': '#00d2d3',
            'is_allergen': False
        },
        {
            'name': 'Orgânico',
            'description': 'Produto orgânico certificado',
            'icon': 'organic',
            'color': '#ff6348',
            'is_allergen': False
        },
        {
            'name': 'Amendoim',
            'description': 'Contém amendoim - alérgeno',
            'icon': 'peanut',
            'color': '#ff4757',
            'is_allergen': True
        },
        {
            'name': 'Soja',
            'description': 'Contém soja - alérgeno',
            'icon': 'soy',
            'color': '#3742fa',
            'is_allergen': True
        }
    ]
    
    def __init__(self, verbose=False):
        """
        Initialize the category setup utility.
        
        Args:
            verbose (bool): Enable verbose output during setup
        """
        self.verbose = verbose
        self.created_restrictions = []
    
    def create_dietary_restrictions(self):
        """
        Create all dietary restrictions if they don't exist.
        
        Returns:
            list: List of created or existing RestricaoAlimentar instances
        """
        if self.verbose:
            print("Setting up dietary restrictions...")
        
        created_restrictions = []
        existing_count = 0
        
        for restriction_data in self.DIETARY_RESTRICTIONS:
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
                    print(f"  ✓ Created: {restriction.name}")
            else:
                existing_count += 1
                if self.verbose:
                    print(f"  - Already exists: {restriction.name}")
        
        self.created_restrictions = created_restrictions
        
        if self.verbose:
            print(f"Dietary restrictions setup complete:")
            print(f"  Created: {len(created_restrictions)}")
            print(f"  Already existed: {existing_count}")
            print(f"  Total available: {RestricaoAlimentar.objects.count()}")
        
        return list(RestricaoAlimentar.objects.all())
    
    def get_categories_list(self):
        """
        Get the list of product categories for use by other generators.
        
        Returns:
            list: List of category dictionaries
        """
        return self.PRODUCT_CATEGORIES.copy()
    
    def get_category_names(self):
        """
        Get just the category names as a list.
        
        Returns:
            list: List of category name strings
        """
        return [category['name'] for category in self.PRODUCT_CATEGORIES]
    
    def get_restrictions_by_type(self, is_allergen=None):
        """
        Get dietary restrictions filtered by allergen status.
        
        Args:
            is_allergen (bool, optional): Filter by allergen status
            
        Returns:
            list: List of restriction dictionaries
        """
        if is_allergen is None:
            return self.DIETARY_RESTRICTIONS.copy()
        
        return [
            restriction for restriction in self.DIETARY_RESTRICTIONS
            if restriction['is_allergen'] == is_allergen
        ]
    
    def get_allergen_restrictions(self):
        """
        Get only allergen-type restrictions.
        
        Returns:
            list: List of allergen restriction dictionaries
        """
        return self.get_restrictions_by_type(is_allergen=True)
    
    def get_dietary_preference_restrictions(self):
        """
        Get only dietary preference restrictions (non-allergens).
        
        Returns:
            list: List of dietary preference restriction dictionaries
        """
        return self.get_restrictions_by_type(is_allergen=False)
    
    def setup_all_categories(self):
        """
        Set up all categories and dietary restrictions.
        
        Returns:
            dict: Summary of setup results
        """
        if self.verbose:
            print("Setting up product categories and dietary restrictions...")
        
        # Create dietary restrictions
        restrictions = self.create_dietary_restrictions()
        
        # Categories are handled as simple strings in the Produto model
        # No separate Category model exists, so we just return the category list
        categories = self.get_categories_list()
        
        summary = {
            'categories_available': len(categories),
            'restrictions_created': len(self.created_restrictions),
            'total_restrictions': len(restrictions),
            'category_names': self.get_category_names()
        }
        
        if self.verbose:
            print(f"\nCategory setup summary:")
            print(f"  Available categories: {summary['categories_available']}")
            print(f"  Categories: {', '.join(summary['category_names'])}")
            print(f"  Dietary restrictions created: {summary['restrictions_created']}")
            print(f"  Total dietary restrictions: {summary['total_restrictions']}")
        
        return summary
    
    def get_setup_summary(self):
        """
        Get a summary of the setup process.
        
        Returns:
            dict: Summary statistics
        """
        return {
            'dietary_restrictions_created': len(self.created_restrictions),
            'total_categories': len(self.PRODUCT_CATEGORIES),
            'total_restrictions_available': len(self.DIETARY_RESTRICTIONS),
            'allergen_restrictions': len(self.get_allergen_restrictions()),
            'preference_restrictions': len(self.get_dietary_preference_restrictions())
        }


def setup_categories_and_restrictions(verbose=False):
    """
    Convenience function to set up all categories and restrictions.
    
    Args:
        verbose (bool): Enable verbose output
        
    Returns:
        tuple: (CategorySetup instance, setup summary dict)
    """
    setup = CategorySetup(verbose=verbose)
    summary = setup.setup_all_categories()
    return setup, summary