import React, { useState, useEffect } from 'react';
import { useCheckout } from '@pedido/shared/hooks/useCheckout';
import DeliveryOptions from '../components/DeliveryOptions';
import AddressSection from '../components/AddressSection';
import PaymentSection from '../components/PaymentSection';
import OrderSummary from '../components/OrderSummary';
import LoadingSpinner from '@components/common/LoadingSpinner';

/**
 * Componente principal do checkout
 * Gerencia todo o fluxo de finalização do pedido
 */
const CheckoutApp = ({ pedidoData, enderecosData, csrfToken }) => {
  const {
    pedido,
    loading,
    error,
    deliveryType,
    paymentMethod,
    selectedAddress,
    updateQuantity,
    removeItem,
    finalizarPedido,
    setDeliveryType,
    setPaymentMethod,
    setSelectedAddress
  } = useCheckout(pedidoData, csrfToken);

  if (loading && !pedido) {
    return <LoadingSpinner message="Carregando checkout..." />;
  }

  if (error) {
    return (
      <div className="alert alert-danger">
        <h4>❌ Erro no Checkout</h4>
        <p>{error}</p>
        <button onClick={() => window.location.reload()} className="btn btn-primary">
          Tentar Novamente
        </button>
      </div>
    );
  }

  const handleSubmit = async (formData) => {
    try {
      await finalizarPedido(formData);
      // Redirecionamento será feito pelo hook
    } catch (error) {
      console.error('Erro ao finalizar pedido:', error);
    }
  };

  return (
    <div className="checkout-container">
      <div className="checkout-header text-center mb-4">
        <h1>🛒 Finalizar Pedido</h1>
        <p className="text-muted">
          Revise seu pedido e complete as informações para finalizar
        </p>
      </div>

      <div className="row">
        {/* Coluna Principal: Formulários */}
        <div className="col-lg-8">
          <form onSubmit={(e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            handleSubmit(formData);
          }}>
            
            {/* Tipo de Entrega */}
            <DeliveryOptions 
              selected={deliveryType}
              onChange={setDeliveryType}
            />
            
            {/* Endereço de Entrega */}
            <AddressSection 
              deliveryType={deliveryType}
              enderecos={enderecosData}
              selectedAddress={selectedAddress}
              onAddressChange={setSelectedAddress}
            />
            
            {/* Método de Pagamento */}
            <PaymentSection 
              selected={paymentMethod}
              onChange={setPaymentMethod}
            />

            {/* Botão de Finalizar */}
            <div className="mt-4">
              <button 
                type="submit" 
                className="btn btn-primary btn-lg w-100"
                disabled={loading || !pedido?.items?.length}
              >
                {loading ? (
                  <>
                    <span className="spinner-border spinner-border-sm me-2" />
                    Processando...
                  </>
                ) : (
                  '🎯 Finalizar Pedido'
                )}
              </button>
            </div>
          </form>
        </div>

        {/* Coluna Lateral: Resumo */}
        <div className="col-lg-4">
          <OrderSummary 
            pedido={pedido}
            deliveryType={deliveryType}
            loading={loading}
            onUpdateQuantity={updateQuantity}
            onRemoveItem={removeItem}
          />
        </div>
      </div>
    </div>
  );
};

export default CheckoutApp;