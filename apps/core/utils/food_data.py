"""
Brazilian fast food data sources for realistic menu generation.

This module contains comprehensive data for Brazilian fast food items including
food items, beverages, nutritional information, and combo meal structures.
"""

import random
from decimal import Decimal


# Brazilian fast food items by category
FOOD_ITEMS = {
    'lanches': [
        {
            'name': 'X-Burger Clássico',
            'description': 'Hambúrguer bovino, queijo, alface, tomate e maionese',
            'base_price': Decimal('12.90'),
            'calories': 450,
            'prep_time': 8,
            'category': 'Lanches'
        },
        {
            'name': 'X-Salada',
            'description': 'Hambúrguer bovino, queijo, alface, tomate, cebola e maionese',
            'base_price': Decimal('14.90'),
            'calories': 480,
            'prep_time': 8,
            'category': 'Lanches'
        },
        {
            'name': 'X-Bacon',
            'description': 'Hambúrguer bovino, queijo, bacon, alface, tomate e maionese',
            'base_price': Decimal('16.90'),
            'calories': 520,
            'prep_time': 10,
            'category': 'Lanches'
        },
        {
            'name': 'X-Tudo',
            'description': 'Hambúrguer bovino, queijo, bacon, ovo, presunto, alface, tomate e maionese',
            'base_price': Decimal('19.90'),
            'calories': 650,
            'prep_time': 12,
            'category': 'Lanches'
        },
        {
            'name': 'Bauru Tradicional',
            'description': 'Presunto, queijo, tomate e orégano no pão francês',
            'base_price': Decimal('11.50'),
            'calories': 380,
            'prep_time': 6,
            'category': 'Lanches'
        },
        {
            'name': 'Misto Quente',
            'description': 'Presunto e queijo no pão de forma tostado',
            'base_price': Decimal('8.90'),
            'calories': 320,
            'prep_time': 5,
            'category': 'Lanches'
        },
        {
            'name': 'Sanduíche Natural',
            'description': 'Peito de peru, queijo branco, alface, tomate e cenoura ralada',
            'base_price': Decimal('9.90'),
            'calories': 280,
            'prep_time': 4,
            'category': 'Lanches'
        },
        {
            'name': 'Cachorro-Quente Simples',
            'description': 'Salsicha, molho de tomate, batata palha e maionese',
            'base_price': Decimal('7.50'),
            'calories': 350,
            'prep_time': 5,
            'category': 'Lanches'
        },
        {
            'name': 'Cachorro-Quente Especial',
            'description': 'Salsicha, molho de tomate, milho, ervilha, batata palha e maionese',
            'base_price': Decimal('10.50'),
            'calories': 420,
            'prep_time': 6,
            'category': 'Lanches'
        }
    ],
    'pizzas': [
        {
            'name': 'Pizza Margherita',
            'description': 'Molho de tomate, mussarela, manjericão e orégano',
            'base_price': Decimal('25.90'),
            'calories': 800,
            'prep_time': 20,
            'category': 'Pizzas'
        },
        {
            'name': 'Pizza Calabresa',
            'description': 'Molho de tomate, mussarela, calabresa e cebola',
            'base_price': Decimal('28.90'),
            'calories': 850,
            'prep_time': 20,
            'category': 'Pizzas'
        },
        {
            'name': 'Pizza Portuguesa',
            'description': 'Molho de tomate, mussarela, presunto, ovos, cebola e azeitona',
            'base_price': Decimal('32.90'),
            'calories': 920,
            'prep_time': 22,
            'category': 'Pizzas'
        },
        {
            'name': 'Pizza Frango com Catupiry',
            'description': 'Molho de tomate, mussarela, frango desfiado e catupiry',
            'base_price': Decimal('30.90'),
            'calories': 880,
            'prep_time': 20,
            'category': 'Pizzas'
        },
        {
            'name': 'Pizza Quatro Queijos',
            'description': 'Molho de tomate, mussarela, provolone, parmesão e catupiry',
            'base_price': Decimal('34.90'),
            'calories': 950,
            'prep_time': 18,
            'category': 'Pizzas'
        }
    ],
    'acompanhamentos': [
        {
            'name': 'Batata Frita Pequena',
            'description': 'Porção individual de batatas fritas crocantes',
            'base_price': Decimal('6.90'),
            'calories': 250,
            'prep_time': 5,
            'category': 'Acompanhamentos'
        },
        {
            'name': 'Batata Frita Grande',
            'description': 'Porção grande de batatas fritas crocantes',
            'base_price': Decimal('9.90'),
            'calories': 400,
            'prep_time': 6,
            'category': 'Acompanhamentos'
        },
        {
            'name': 'Onion Rings',
            'description': 'Anéis de cebola empanados e fritos',
            'base_price': Decimal('8.50'),
            'calories': 320,
            'prep_time': 6,
            'category': 'Acompanhamentos'
        },
        {
            'name': 'Nuggets de Frango',
            'description': '8 unidades de nuggets de frango empanados',
            'base_price': Decimal('12.90'),
            'calories': 380,
            'prep_time': 7,
            'category': 'Acompanhamentos'
        },
        {
            'name': 'Salada Verde',
            'description': 'Mix de folhas verdes, tomate cereja e molho à parte',
            'base_price': Decimal('7.50'),
            'calories': 80,
            'prep_time': 3,
            'category': 'Acompanhamentos'
        }
    ],
    'sobremesas': [
        {
            'name': 'Sorvete de Baunilha',
            'description': '2 bolas de sorvete de baunilha com calda de chocolate',
            'base_price': Decimal('8.90'),
            'calories': 280,
            'prep_time': 2,
            'category': 'Sobremesas'
        },
        {
            'name': 'Brownie com Sorvete',
            'description': 'Brownie de chocolate quente com sorvete de baunilha',
            'base_price': Decimal('12.90'),
            'calories': 450,
            'prep_time': 3,
            'category': 'Sobremesas'
        },
        {
            'name': 'Pudim de Leite',
            'description': 'Pudim de leite condensado com calda de caramelo',
            'base_price': Decimal('6.90'),
            'calories': 220,
            'prep_time': 1,
            'category': 'Sobremesas'
        },
        {
            'name': 'Torta de Limão',
            'description': 'Fatia de torta de limão com merengue',
            'base_price': Decimal('9.90'),
            'calories': 320,
            'prep_time': 2,
            'category': 'Sobremesas'
        }
    ]
}

# Beverage data with sizes and types
BEVERAGES = [
    {
        'name': 'Coca-Cola',
        'description': 'Refrigerante de cola',
        'category': 'Refrigerantes',
        'sizes': {
            'Pequeno (300ml)': {'price': Decimal('4.50'), 'calories': 126},
            'Médio (500ml)': {'price': Decimal('6.50'), 'calories': 210},
            'Grande (700ml)': {'price': Decimal('8.50'), 'calories': 294}
        },
        'prep_time': 1
    },
    {
        'name': 'Guaraná Antarctica',
        'description': 'Refrigerante de guaraná',
        'category': 'Refrigerantes',
        'sizes': {
            'Pequeno (300ml)': {'price': Decimal('4.50'), 'calories': 120},
            'Médio (500ml)': {'price': Decimal('6.50'), 'calories': 200},
            'Grande (700ml)': {'price': Decimal('8.50'), 'calories': 280}
        },
        'prep_time': 1
    },
    {
        'name': 'Fanta Laranja',
        'description': 'Refrigerante sabor laranja',
        'category': 'Refrigerantes',
        'sizes': {
            'Pequeno (300ml)': {'price': Decimal('4.50'), 'calories': 132},
            'Médio (500ml)': {'price': Decimal('6.50'), 'calories': 220},
            'Grande (700ml)': {'price': Decimal('8.50'), 'calories': 308}
        },
        'prep_time': 1
    },
    {
        'name': 'Suco de Laranja Natural',
        'description': 'Suco de laranja natural sem açúcar',
        'category': 'Sucos Naturais',
        'sizes': {
            'Pequeno (300ml)': {'price': Decimal('6.90'), 'calories': 84},
            'Médio (500ml)': {'price': Decimal('9.90'), 'calories': 140}
        },
        'prep_time': 3
    },
    {
        'name': 'Suco de Acerola',
        'description': 'Suco de acerola natural rico em vitamina C',
        'category': 'Sucos Naturais',
        'sizes': {
            'Pequeno (300ml)': {'price': Decimal('7.50'), 'calories': 90},
            'Médio (500ml)': {'price': Decimal('10.50'), 'calories': 150}
        },
        'prep_time': 3
    },
    {
        'name': 'Água Mineral',
        'description': 'Água mineral sem gás',
        'category': 'Águas',
        'sizes': {
            'Pequeno (300ml)': {'price': Decimal('2.50'), 'calories': 0},
            'Grande (500ml)': {'price': Decimal('3.50'), 'calories': 0}
        },
        'prep_time': 1
    },
    {
        'name': 'Água com Gás',
        'description': 'Água mineral com gás',
        'category': 'Águas',
        'sizes': {
            'Pequeno (300ml)': {'price': Decimal('3.00'), 'calories': 0},
            'Grande (500ml)': {'price': Decimal('4.00'), 'calories': 0}
        },
        'prep_time': 1
    },
    {
        'name': 'Café Expresso',
        'description': 'Café expresso tradicional',
        'category': 'Cafés',
        'sizes': {
            'Simples (50ml)': {'price': Decimal('3.50'), 'calories': 5},
            'Duplo (100ml)': {'price': Decimal('5.50'), 'calories': 10}
        },
        'prep_time': 2
    },
    {
        'name': 'Cappuccino',
        'description': 'Café com leite vaporizado e canela',
        'category': 'Cafés',
        'sizes': {
            'Médio (200ml)': {'price': Decimal('7.90'), 'calories': 120},
            'Grande (300ml)': {'price': Decimal('9.90'), 'calories': 180}
        },
        'prep_time': 4
    },
    {
        'name': 'Milkshake de Chocolate',
        'description': 'Milkshake cremoso sabor chocolate',
        'category': 'Milkshakes',
        'sizes': {
            'Médio (400ml)': {'price': Decimal('12.90'), 'calories': 380},
            'Grande (600ml)': {'price': Decimal('16.90'), 'calories': 570}
        },
        'prep_time': 5
    },
    {
        'name': 'Milkshake de Morango',
        'description': 'Milkshake cremoso sabor morango',
        'category': 'Milkshakes',
        'sizes': {
            'Médio (400ml)': {'price': Decimal('12.90'), 'calories': 360},
            'Grande (600ml)': {'price': Decimal('16.90'), 'calories': 540}
        },
        'prep_time': 5
    }
]

# Combo meal templates with discount structures
COMBO_TEMPLATES = [
    {
        'name': 'Combo X-Burger',
        'description': 'X-Burger Clássico + Batata Frita + Refrigerante',
        'main_items': ['X-Burger Clássico'],
        'side_items': ['Batata Frita Pequena'],
        'drink_categories': ['Refrigerantes'],
        'drink_sizes': ['Médio (500ml)'],
        'discount_percent': 15,
        'category': 'Combos'
    },
    {
        'name': 'Combo X-Salada',
        'description': 'X-Salada + Batata Frita + Refrigerante',
        'main_items': ['X-Salada'],
        'side_items': ['Batata Frita Pequena'],
        'drink_categories': ['Refrigerantes'],
        'drink_sizes': ['Médio (500ml)'],
        'discount_percent': 15,
        'category': 'Combos'
    },
    {
        'name': 'Combo X-Bacon',
        'description': 'X-Bacon + Batata Frita Grande + Refrigerante',
        'main_items': ['X-Bacon'],
        'side_items': ['Batata Frita Grande'],
        'drink_categories': ['Refrigerantes'],
        'drink_sizes': ['Grande (700ml)'],
        'discount_percent': 18,
        'category': 'Combos'
    },
    {
        'name': 'Combo Família Pizza',
        'description': 'Pizza Grande + 2 Refrigerantes + Sobremesa',
        'main_items': ['Pizza Margherita', 'Pizza Calabresa', 'Pizza Portuguesa'],
        'side_items': ['Sorvete de Baunilha', 'Pudim de Leite'],
        'drink_categories': ['Refrigerantes'],
        'drink_sizes': ['Grande (700ml)'],
        'drink_quantity': 2,
        'discount_percent': 20,
        'category': 'Combos'
    },
    {
        'name': 'Combo Kids',
        'description': 'Nuggets + Batata Pequena + Suco + Sorvete',
        'main_items': ['Nuggets de Frango'],
        'side_items': ['Batata Frita Pequena'],
        'drink_categories': ['Sucos Naturais'],
        'drink_sizes': ['Pequeno (300ml)'],
        'dessert_items': ['Sorvete de Baunilha'],
        'discount_percent': 12,
        'category': 'Combos'
    }
]

# Dietary restrictions mapping
DIETARY_RESTRICTIONS = [
    {'name': 'Glúten', 'description': 'Contém glúten'},
    {'name': 'Lactose', 'description': 'Contém lactose'},
    {'name': 'Vegano', 'description': 'Produto vegano'},
    {'name': 'Vegetariano', 'description': 'Produto vegetariano'},
    {'name': 'Sem Açúcar', 'description': 'Produto sem açúcar adicionado'},
    {'name': 'Sem Gordura Trans', 'description': 'Produto sem gordura trans'},
    {'name': 'Rico em Fibras', 'description': 'Produto rico em fibras'},
    {'name': 'Fonte de Proteína', 'description': 'Produto fonte de proteína'}
]


def get_all_food_items():
    """
    Get all food items from all categories.
    
    Returns:
        list: List of all food item dictionaries
    """
    all_items = []
    for category_items in FOOD_ITEMS.values():
        all_items.extend(category_items)
    return all_items


def get_food_items_by_category(category):
    """
    Get food items from a specific category.
    
    Args:
        category (str): Category name ('lanches', 'pizzas', 'acompanhamentos', 'sobremesas')
        
    Returns:
        list: List of food items in the specified category
    """
    return FOOD_ITEMS.get(category, [])


def get_random_food_item():
    """
    Get a random food item from any category.
    
    Returns:
        dict: Random food item dictionary
    """
    all_items = get_all_food_items()
    return random.choice(all_items)


def get_random_beverage():
    """
    Get a random beverage.
    
    Returns:
        dict: Random beverage dictionary
    """
    return random.choice(BEVERAGES)


def get_beverages_by_category(category):
    """
    Get beverages from a specific category.
    
    Args:
        category (str): Category name ('Refrigerantes', 'Sucos Naturais', 'Águas', 'Cafés', 'Milkshakes')
        
    Returns:
        list: List of beverages in the specified category
    """
    return [bev for bev in BEVERAGES if bev['category'] == category]


def get_random_combo_template():
    """
    Get a random combo meal template.
    
    Returns:
        dict: Random combo template dictionary
    """
    return random.choice(COMBO_TEMPLATES)


def calculate_combo_price(combo_template, selected_items):
    """
    Calculate the final price of a combo meal with discount applied.
    
    Args:
        combo_template (dict): Combo template with discount information
        selected_items (list): List of selected item prices
        
    Returns:
        Decimal: Final combo price with discount applied
    """
    total_price = sum(selected_items)
    discount = total_price * (combo_template['discount_percent'] / 100)
    return total_price - discount


def get_random_dietary_restrictions(max_restrictions=3):
    """
    Get a random set of dietary restrictions.
    
    Args:
        max_restrictions (int): Maximum number of restrictions to return
        
    Returns:
        list: List of dietary restriction dictionaries
    """
    num_restrictions = random.randint(0, max_restrictions)
    return random.sample(DIETARY_RESTRICTIONS, num_restrictions)