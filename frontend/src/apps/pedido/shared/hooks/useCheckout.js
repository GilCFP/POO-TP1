import { useState, useCallback } from 'react';
import { pedidoService } from '../services/pedidoService';

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
  const updateQuantity = useCallback(async (produtoId, newQuantity) => {
    if (newQuantity < 1 || !pedido) return;

    setLoading(true);
    setError(null);

    try {
      const getCSRFToken = () => {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : csrfToken;
      };

      const response = await pedidoService.atualizarQuantidadeItem(
        pedido.id,
        produtoId,
        newQuantidade,
        getCSRFToken()
      );

      if (response.success) {
        // Recarregar dados do pedido
        const pedidoAtualizado = await pedidoService.obterPedido(pedido.id);
        if (pedidoAtualizado.success) {
          setPedido(pedidoAtualizado.pedido);
        }
      } else {
        throw new Error(response.error || 'Erro ao atualizar quantidade');
      }
    } catch (err) {
      setError(err.message);
      console.error('Erro ao atualizar quantidade:', err);
    } finally {
      setLoading(false);
    }
  }, [pedido, csrfToken]);

  /**
   * Remove item do pedido
   */
  const removeItem = useCallback(async (produtoId) => {
    if (!pedido) return;

    setLoading(true);
    setError(null);

    try {
      const getCSRFToken = () => {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : csrfToken;
      };

      const response = await pedidoService.removerItem(
        pedido.id,
        produtoId,
        getCSRFToken()
      );

      if (response.success) {
        // Recarregar dados do pedido
        const pedidoAtualizado = await pedidoService.obterPedido(pedido.id);
        if (pedidoAtualizado.success) {
          setPedido(pedidoAtualizado.pedido);
        }
      } else {
        throw new Error(response.error || 'Erro ao remover item');
      }
    } catch (err) {
      setError(err.message);
      console.error('Erro ao remover item:', err);
    } finally {
      setLoading(false);
    }
  }, [pedido, csrfToken]);

  /**
   * Finaliza o pedido
   */
  const finalizarPedido = useCallback(async (formData) => {
    if (!pedido) return;

    setLoading(true);
    setError(null);

    try {
      const getCSRFToken = () => {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : csrfToken;
      };

      // Primeiro finaliza o pedido (muda para aguardando pagamento)
      const finalizeResponse = await pedidoService.finalizarPedido(
        pedido.id,
        getCSRFToken()
      );

      if (!finalizeResponse.success) {
        throw new Error(finalizeResponse.error || 'Erro ao finalizar pedido');
      }

      // Depois processa o pagamento
      const paymentResponse = await pedidoService.processarPagamento(
        pedido.id,
        paymentMethod,
        getCSRFToken()
      );

      if (paymentResponse.success) {
        // Sucesso - redireciona para status do pedido
        window.location.href = `/pedido/${pedido.id}/status/`;
      } else {
        throw new Error(paymentResponse.error || 'Erro ao processar pagamento');
      }
    } catch (err) {
      setError(err.message);
      console.error('Erro ao finalizar pedido:', err);
    } finally {
      setLoading(false);
    }
  }, [pedido, deliveryType, paymentMethod, selectedAddress, csrfToken]);

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