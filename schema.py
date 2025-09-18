from enum import Enum

class StatusPedido(Enum):
    CANCELED = -1
    ORDERING = 0
    PENDING_PAYMENT = 1
    WAITING = 2
    PREPARING = 3
    READY = 4
    BEING_DELIVERED = 5
    DELIVERED = 6
    
class RestricaoAlimentar(Enum):
    NONE = 1
    VEGETARIAN = 2
    VEGAN = 3
    GLUTEN_FREE = 4
    NUT_ALLERGY = 5
    DAIRY_FREE = 6
    HALAL = 7
    KOSHER = 8

class Produto:
    def __init__(self, name:str, price, available:bool=True):
        self.name = name
        self.id = id(self)
        self.price = price
        self.available = available

    def apply_discount(self, discount):
        if 0 <= discount <= 1:
            self.price *= (1 - discount)
        else:
            raise ValueError("Discount must be between 0 and 1")

    def __repr__(self):
        return f"Product(name={self.name}, price={self.price:.2f})"
    
class Alimento(Produto):
    def __init__(self, name:str, price:float, expiration_date:str, calories:int, time_to_prepare:int=0, available:bool=True, alimentary_restrictions:list[RestricaoAlimentar]=[], is_ingredient:bool=False):
        super().__init__(name, price, available)
        self.expiration_date = expiration_date
        self.calories = calories
        self.time_to_prepare = time_to_prepare
        self.alimentary_restrictions = alimentary_restrictions
        self.is_ingredient = is_ingredient
        self.additional_ingredients = []

    def is_expired(self, current_date:str):
        return current_date > self.expiration_date
    
    def add_ingredient(self, ingredient:"Alimento"):
        
        if self.is_ingredient:
            raise ValueError("Cannot add ingredients to an ingredient")
        
        if not ingredient.is_ingredient:
            raise ValueError("Ingredient must be marked as an ingredient")
        
        self.additional_ingredients.append(ingredient)
        self.alimentary_restrictions.extend(ingredient.alimentary_restrictions)
        self.calories += ingredient.calories
    
    def remove_ingredient(self, ingredient:"Alimento"):
        if ingredient in self.additional_ingredients:
            self.additional_ingredients.remove(ingredient)
            self.alimentary_restrictions = [r for r in self.alimentary_restrictions if r not in ingredient.alimentary_restrictions]
            self.calories -= ingredient.calories
        else:
            raise ValueError("Ingredient not found in the food item")
    
    def __repr__(self):
        
        return f"Food(name={self.name}, price={self.price:.2f}, expiration_date={self.expiration_date}, time_to_prepare={self.time_to_prepare})"

class Comida(Alimento):
    def __init__(self, name:str, price:float, expiration_date:str, calories:int, persons_served:int, time_to_prepare:int=0, available:bool=True, alimentary_restrictions:list[RestricaoAlimentar]=[], is_ingredient:bool=False):
        super().__init__(name, price, expiration_date, calories, time_to_prepare, available, alimentary_restrictions, is_ingredient)
        self.persons_served = persons_served
        
class Bebida(Alimento):
    def __init__(self, name:str, price:float, expiration_date:str, calories:int, volume_ml:int, is_alcoholic:bool, time_to_prepare:int=0, available:bool=True, alimentary_restrictions:list[RestricaoAlimentar]=[], is_ingredient:bool=False):
        super().__init__(name, price, expiration_date, calories, time_to_prepare, available, alimentary_restrictions)
        self.volume_ml = volume_ml
        self.is_alcoholic = is_alcoholic
        self.is_ingredient = is_ingredient

class Combo:
    def __init__(self, name:str, items:list[Produto]):
        self.name = name
        self.items = items
        self.price = sum(item.price for item in items)

    def apply_discount(self, discount):
        if 0 <= discount <= 1:
            self.price *= (1 - discount)
        else:
            raise ValueError("Discount must be between 0 and 1")
        
    def get_time_to_prepare(self):
        return sum(item.time_to_prepare for item in self.items if isinstance(item, Alimento))

    def __repr__(self):
        return f"Combo(name={self.name}, price={self.price:.2f}, items={self.items})"

class Pedido:
    def __init__(self, status:StatusPedido=StatusPedido.ORDERING, id:int=None):
        self.items = []
        self.total_price = 0.0
        self.status = status
        self.id = id

    def add_item(self, item):
        self.items.append(item)
        self.total_price += item.price

    def remove_item(self, item):
        if item in self.items:
            self.items.remove(item)
            self.total_price -= item.price
        else:
            raise ValueError("Item not in order")
    
    def change_status(self, new_status:StatusPedido):
        if new_status < self.status and new_status != StatusPedido.CANCELED:
            raise ValueError("Cannot revert to a previous status")
        self.status = new_status
        
    def go_to_next_status(self):
        if self.status == StatusPedido.CANCELED:
            raise ValueError("Cannot change status of a canceled order")
        elif self.status == StatusPedido.DELIVERED:
            raise ValueError("Order is already delivered")
        else:
            self.status = StatusPedido(self.status.value + 1)
    
    def get_total(self):
        return self.total_price

    def __repr__(self):
        return f"Order(total_price={self.total_price:.2f}, items={self.items})"

class Cliente:
    
    def __init__(self, name:str, balance:float=0.0, cart:Pedido=None, address:str=None):
        self.name = name
        self.balance = balance
        self.cart = cart if cart is not None else Pedido()
        self.address = address
        self.alimentary_restrictions: list[RestricaoAlimentar] = []

    
    def add_alimentary_restriction(self, restriction:RestricaoAlimentar):
        if restriction not in self.alimentary_restrictions:
            self.alimentary_restrictions.append(restriction)

    def remove_alimentary_restriction(self, restriction:RestricaoAlimentar):
        if restriction in self.alimentary_restrictions:
            self.alimentary_restrictions.remove(restriction)

    def clear_alimentary_restrictions(self):
        self.alimentary_restrictions.clear()

    def can_consume(self, product:Produto):
        if isinstance(product, Alimento):
            for restriction in self.alimentary_restrictions:
                if restriction in product.alimentary_restrictions:
                    return False
        return True
    
    def _add_funds(self, amount:float):
        if amount > 0:
            self.balance += amount
        else:
            raise ValueError("Amount must be positive")
    
    def _remove_funds(self, amount:float):
        if 0 < amount <= self.balance:
            self.balance -= amount
        else:
            raise ValueError("Insufficient funds or invalid amount")
    
    def pay_cart(self):
        order_total = self.cart.get_total()
        if self.balance >= order_total:
            self._remove_funds(order_total)
            self.cart.change_status(StatusPedido.PENDING_PAYMENT)
        else:
            raise ValueError("Insufficient funds to pay for the cart")

    def __repr__(self):
        return f"Client(name={self.name}, balance={self.balance:.2f}, cart={self.cart})"

class Caixa:
    def __init__(self, initial_cash:float=0.0):
        self.total_revenue = initial_cash

    def process_payment(self, client:Cliente):
        order_total = client.cart.get_total()
        if client.balance >= order_total:
            client._remove_funds(order_total)
            self.total_revenue += order_total
            client.cart = Pedido()
        else:
            raise ValueError("Insufficient funds for payment")

    def __repr__(self):
        return f"CashRegister(total_revenue={self.total_revenue:.2f})"

class Restaurante:
    def __init__(self, initial_cash:float=0.0):
        self.menu = []
        self.clients = []
        self.cash_register = Caixa(initial_cash)
        

    def add_product_to_menu(self, product:Produto):
        self.menu.append(product)

    def register_client(self, client:Cliente):
        self.clients.append(client)

    def __repr__(self):
        return f"Restaurant(menu={self.menu}, clients={self.clients}, cash_register={self.cash_register})"

class Cozinha:
    def __init__(self, number_of_chefs:int=1):
        self.orders_in_progress = {}
        self.orders_in_queue: list[Pedido] = []
        self.number_of_orders_in_progress = 0
        self.number_of_chefs = number_of_chefs
        self.full_capacity = number_of_chefs

    def start_next_order(self):
        
        if self.number_of_orders_in_progress == self.full_capacity:
            raise ValueError("Kitchen is at full capacity")
        
        if not self.orders_in_queue:
            raise ValueError("No orders in queue")
        
        order = self.orders_in_queue.pop(0)
        order.go_to_next_status()
        self.orders_in_progress[order.id] = order
        self.number_of_orders_in_progress += 1

    def add_order_to_queue(self, order:Pedido):
        if order.status != StatusPedido.PENDING_PAYMENT:
            raise ValueError("Only orders with status PENDING_PAYMENT can be added to the queue")
        self.orders_in_queue.append(order)

    def add_priority_order_to_queue(self, order:Pedido):
        if order.status != StatusPedido.PENDING_PAYMENT:
            raise ValueError("Only orders with status PENDING_PAYMENT can be added to the queue")
        self.orders_in_queue.insert(0, order)
        
    def complete_order(self, order:Pedido):
        if order.id in self.orders_in_progress:
            del self.orders_in_progress[order.id]
            self.number_of_orders_in_progress -= 1
            order.go_to_next_status()
            
        else:
            raise ValueError("Order not found in progress")