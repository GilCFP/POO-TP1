import { useState, useCallback } from 'react';
import { apiService } from '@shared/services/api';

/**
 * Hook personalizado para gerenciar estado e ações do checkout
 */
export const useCheckout = (initialPedido, csrfToken) => {
  const [pedido, setPedido] = useState(initialPedido);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [deliveryType, setDeliveryType] = useState('delivery');
  const [paymentMethod, setPaymentMethod] = useState('credit_card');
  const [selectedAddress, setSelectedAddress] = useState('saved1');

  /**
   * Atualiza quantidade de um item
   */
  const updateQuantity = useCallback(async (itemId, newQuantity) => {
    if (newQuantity < 1) return;

    setLoading(true);
    setError(null);

    try {
      const response = await apiService.post('/pedido/update-item/', {
        item_id: itemId,
        quantity: newQuantity
      }, csrfToken);

      if (response.success) {
        setPedido(response.pedido);
      } else {
        throw new Error(response.error || 'Erro ao atualizar quantidade');
      }
    } catch (err) {
      setError(err.message);
      console.error('Erro ao atualizar quantidade:', err);
    } finally {
      setLoading(false);
    }
  }, [csrfToken]);

  /**
   * Remove item do pedido
   */
  const removeItem = useCallback(async (itemId) => {
    setLoading(true);
    setError(null);

    try {
      const response = await apiService.post('/pedido/remove-item/', {
        item_id: itemId
      }, csrfToken);

      if (response.success) {
        setPedido(response.pedido);
      } else {
        throw new Error(response.error || 'Erro ao remover item');
      }
    } catch (err) {
      setError(err.message);
      console.error('Erro ao remover item:', err);
    } finally {
      setLoading(false);
    }
  }, [csrfToken]);

  /**
   * Finaliza o pedido
   */
  const finalizarPedido = useCallback(async (formData) => {
    setLoading(true);
    setError(null);

    try {
      // Adiciona dados do estado ao FormData
      formData.append('delivery_type', deliveryType);
      formData.append('payment_method', paymentMethod);
      formData.append('selected_address', selectedAddress);
      formData.append('csrfmiddlewaretoken', csrfToken);

      const response = await fetch('/pedido/finalizar/', {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        // Sucesso - redireciona para confirmação
        const data = await response.json();
        window.location.href = data.redirect_url || '/pedido/confirmacao/';
      } else {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Erro ao processar pedido');
      }
    } catch (err) {
      setError(err.message);
      console.error('Erro ao finalizar pedido:', err);
    } finally {
      setLoading(false);
    }
  }, [deliveryType, paymentMethod, selectedAddress, csrfToken]);

  return {
    // Estado
    pedido,
    loading,
    error,
    deliveryType,
    paymentMethod,
    selectedAddress,

    // Ações
    updateQuantity,
    removeItem,
    finalizarPedido,
    setDeliveryType,
    setPaymentMethod,
    setSelectedAddress,
    
    // Helpers
    clearError: () => setError(null)
  };
};