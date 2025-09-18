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