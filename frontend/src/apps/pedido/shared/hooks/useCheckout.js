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
    if (newQuantity < 1 || !pedido) {
      console.error('Parâmetros inválidos:', { produtoId, newQuantity, pedido });
      return;
    }

    console.log('updateQuantity chamado:', { produtoId, newQuantity, pedidoId: pedido.id });

    setLoading(true);
    setError(null);

    try {
      const getCSRFToken = () => {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : csrfToken;
      };

      console.log('Chamando atualizarQuantidadeItem:', {
        pedidoId: pedido.id,
        produtoId,
        newQuantity,
        csrfToken: getCSRFToken()
      });

      const response = await pedidoService.atualizarQuantidadeItem(
        pedido.id,
        produtoId,
        newQuantity,
        getCSRFToken()
      );

      console.log('Resposta da API:', response);

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
      console.error('Erro detalhado:', err);
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

    console.log('removeItem chamado:', { produtoId, pedidoId: pedido.id });

    setLoading(true);
    setError(null);

    try {
      const getCSRFToken = () => {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : csrfToken;
      };

      console.log('Chamando removerItem:', {
        pedidoId: pedido.id,
        produtoId,
        csrfToken: getCSRFToken()
      });

      const response = await pedidoService.removerItem(
        pedido.id,
        produtoId,
        getCSRFToken()
      );

      console.log('Resposta do removerItem:', response);

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
      console.error('Erro detalhado ao remover item:', err);
      setError(err.message);
      console.error('Erro ao remover item:', err);
    } finally {
      setLoading(false);
    }
  }, [pedido, csrfToken]);

  /**
   * Finaliza o pedido fazendo chamadas reais para o backend
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

      console.log('Finalizando pedido:', pedido.id);

      // 1. Primeiro finaliza o pedido (muda status de ORDERING para PENDING_PAYMENT)
      const finalizeResponse = await fetch(`/api/pedidos/${pedido.id}/finalizar/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({
          delivery_type: deliveryType,
          delivery_address: deliveryType === 'delivery' ? formData.get('delivery_address') || 'Endereço do cliente' : null
        })
      });

      const finalizeData = await finalizeResponse.json();
      console.log('Resposta do finalizar:', finalizeData);

      if (!finalizeData.success) {
        throw new Error(finalizeData.error || 'Erro ao finalizar pedido');
      }

      // 2. Depois processa o pagamento (muda para status seguinte)
      const paymentResponse = await fetch(`/api/pedidos/processar-pagamento/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({
          pedido_id: pedido.id,
          metodo_pagamento: paymentMethod
        })
      });

      const paymentData = await paymentResponse.json();
      console.log('Resposta do pagamento:', paymentData);

      if (!paymentData.success) {
        throw new Error(paymentData.error || 'Erro ao processar pagamento');
      }

      // Sucesso - mostra mensagem e redireciona
      alert(`✅ Pedido finalizado com sucesso!\n\n` +
            `Tipo: ${deliveryType === 'pickup' ? 'Retirada' : 'Entrega'}\n` +
            `Pagamento: ${paymentMethod === 'card' ? 'Cartão' : paymentMethod === 'pix' ? 'PIX' : 'Dinheiro'}\n` +
            `Total: R$ ${(pedido.total_price || 0).toFixed(2)}`);
      
      // Constrói a URL corretamente e redireciona
      const statusUrl = `/pedidos/${pedido.id}/status/`;
      console.log('Redirecionando para:', statusUrl);
      window.location.href = statusUrl;
      
    } catch (err) {
      setError(err.message || 'Erro ao finalizar pedido. Tente novamente.');
      console.error('Erro ao finalizar pedido:', err);
    } finally {
      setLoading(false);
    }
  }, [pedido, deliveryType, paymentMethod, csrfToken]);

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