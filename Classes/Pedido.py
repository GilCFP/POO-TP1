from StatusPedido import StatusPedido


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