import { getCsrfToken } from '../../../../shared/utils/csrf';

/**
 * Serviço para comunicação com APIs do kanban do restaurante
 */
class KanbanService {
    constructor() {
        this.baseUrl = '/api/restaurante/kanban';
    }

    /**
     * Busca dados atuais dos pedidos organizados por status
     */
    async fetchOrders() {
        try {
            const response = await fetch(`${this.baseUrl}/orders/`);
            
            if (!response.ok) {
                throw new Error(`Erro HTTP: ${response.status}`);
            }
            
            const data = await response.json();
            return {
                success: true,
                data
            };
        } catch (error) {
            console.error('Erro ao buscar pedidos:', error);
            return {
                success: false,
                error: error.message || 'Erro ao carregar pedidos'
            };
        }
    }

    /**
     * Avança o status de um pedido para o próximo estágio
     */
    async advanceOrderStatus(orderId) {
        try {
            const response = await fetch(`/api/pedidos/_pedido/${orderId}/avancar-status/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                }
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `Erro HTTP: ${response.status}`);
            }

            const data = await response.json();
            return {
                success: true,
                data
            };
        } catch (error) {
            console.error('Erro ao avançar status:', error);
            return {
                success: false,
                error: error.message || 'Erro ao avançar status do pedido'
            };
        }
    }

    /**
     * Atualiza o status de um pedido para um status específico
     */
    async updateOrderStatus(orderId, newStatus) {
        try {
            const response = await fetch(`/api/pedidos/_pedido/${orderId}/atualizar-status/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify({ status: newStatus })
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `Erro HTTP: ${response.status}`);
            }

            const data = await response.json();
            return {
                success: true,
                data
            };
        } catch (error) {
            console.error('Erro ao atualizar status:', error);
            return {
                success: false,
                error: error.message || 'Erro ao atualizar status do pedido'
            };
        }
    }

    /**
     * Busca métricas da cozinha
     */
    async fetchMetrics() {
        try {
            const response = await fetch(`${this.baseUrl}/metrics/`);
            
            if (!response.ok) {
                throw new Error(`Erro HTTP: ${response.status}`);
            }
            
            const data = await response.json();
            return {
                success: true,
                data
            };
        } catch (error) {
            console.error('Erro ao buscar métricas:', error);
            return {
                success: false,
                error: error.message || 'Erro ao carregar métricas'
            };
        }
    }
}

// Instância singleton do serviço
const kanbanService = new KanbanService();

export default kanbanService;