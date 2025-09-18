from Pedido import Pedido
from StatusPedido import StatusPedido


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