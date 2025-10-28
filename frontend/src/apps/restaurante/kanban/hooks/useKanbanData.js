import { useState, useCallback } from 'react';
import kanbanService from '../services/kanbanService';

/**
 * Hook customizado para gerenciar dados do kanban
 */
export const useKanbanData = (initialData) => {
    const [ordersByStatus, setOrdersByStatus] = useState(initialData?.orders_by_status || {});
    const [statusChoices] = useState(initialData?.status_choices || []);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [updatingOrders, setUpdatingOrders] = useState(new Set());

    /**
     * Recarrega os dados dos pedidos
     */
    const refreshOrders = useCallback(async () => {
        setLoading(true);
        setError(null);
        
        const result = await kanbanService.fetchOrders();
        
        if (result.success) {
            setOrdersByStatus(result.data.orders_by_status || {});
        } else {
            setError(result.error);
        }
        
        setLoading(false);
    }, []);

    /**
     * Avança o status de um pedido
     */
    const advanceOrder = useCallback(async (orderId) => {
        setUpdatingOrders(prev => new Set([...prev, orderId]));
        setError(null);
        
        const result = await kanbanService.advanceOrderStatus(orderId);
        
        if (result.success) {
            // Recarregar dados após sucesso
            await refreshOrders();
        } else {
            setError(result.error);
        }
        
        setUpdatingOrders(prev => {
            const newSet = new Set(prev);
            newSet.delete(orderId);
            return newSet;
        });
        
        return result.success;
    }, [refreshOrders]);

    /**
     * Atualiza o status de um pedido para um status específico
     */
    const updateOrderStatus = useCallback(async (orderId, newStatus) => {
        setUpdatingOrders(prev => new Set([...prev, orderId]));
        setError(null);
        
        const result = await kanbanService.updateOrderStatus(orderId, newStatus);
        
        if (result.success) {
            // Recarregar dados após sucesso
            await refreshOrders();
        } else {
            setError(result.error);
        }
        
        setUpdatingOrders(prev => {
            const newSet = new Set(prev);
            newSet.delete(orderId);
            return newSet;
        });
        
        return result.success;
    }, [refreshOrders]);

    /**
     * Verifica se um pedido específico está sendo atualizado
     */
    const isOrderUpdating = useCallback((orderId) => {
        return updatingOrders.has(orderId);
    }, [updatingOrders]);

    /**
     * Limpa o erro atual
     */
    const clearError = useCallback(() => {
        setError(null);
    }, []);

    return {
        ordersByStatus,
        statusChoices,
        loading,
        error,
        refreshOrders,
        advanceOrder,
        updateOrderStatus,
        isOrderUpdating,
        clearError
    };
};