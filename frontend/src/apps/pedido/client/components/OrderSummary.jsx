import React from 'react';
import clsx from 'clsx';

/**
 * Componente para resumo do pedido com controles
 */
const OrderSummary = ({ 
  pedido, 
  deliveryType, 
  loading, 
  onUpdateQuantity, 
  onRemoveItem 
}) => {
  if (!pedido) {
    return (
      <div className="order-summary">
        <div className="summary-card">
          <div className="summary-header">
            <h5 className="mb-0">📋 Resumo do Pedido</h5>
          </div>
          <div className="summary-body text-center">
            <p className="text-muted">Carregando pedido...</p>
          </div>
        </div>
      </div>
    );
  }

  const deliveryFee = deliveryType === 'pickup' ? 0 : 5.00;
  const subtotal = pedido.items?.reduce((sum, item) => sum + (item.subtotal || 0), 0) || 0;
  const total = subtotal + deliveryFee;

  const handleQuantityChange = (itemId, change) => {
    const item = pedido.items.find(i => i.id === itemId);
    if (!item) return;

    const newQuantity = item.quantidade + change;
    if (newQuantity >= 1) {
      onUpdateQuantity(itemId, newQuantity);
    }
  };

  const handleRemove = (itemId) => {
    const item = pedido.items.find(i => i.id === itemId);
    if (!item) return;

    if (confirm(`Remover "${item.produto?.nome}" do pedido?`)) {
      onRemoveItem(itemId);
    }
  };

  return (
    <div className="order-summary">
      <div className={clsx('summary-card', { 'loading-overlay': loading })}>
        <div className="summary-header">
          <h5 className="mb-0">📋 Resumo do Pedido</h5>
        </div>
        
        <div className="summary-body">
          {/* Lista de Itens */}
          <div className="cart-items">
            {pedido.items?.length > 0 ? (
              pedido.items.map((item) => (
                <CartItem
                  key={item.id}
                  item={item}
                  onQuantityChange={handleQuantityChange}
                  onRemove={handleRemove}
                  disabled={loading}
                />
              ))
            ) : (
              <div className="text-center text-muted py-3">
                <p>🛒 Carrinho vazio</p>
                <a href="/cardapio" className="btn btn-outline-primary btn-sm">
                  Adicionar Itens
                </a>
              </div>
            )}
          </div>

          {/* Totais */}
          {pedido.items?.length > 0 && (
            <div className="summary-totals">
              <div className="total-line">
                <span>Subtotal:</span>
                <span>R$ {subtotal.toFixed(2)}</span>
              </div>
              <div className="total-line">
                <span>Taxa de entrega:</span>
                <span>R$ {deliveryFee.toFixed(2)}</span>
              </div>
              <div className="total-line final">
                <span>Total:</span>
                <span className="amount">R$ {total.toFixed(2)}</span>
              </div>
            </div>
          )}
        </div>

        {/* Ações */}
        <div className="card-footer bg-light">
          <a 
            href="/cardapio" 
            className="btn btn-outline-secondary w-100 mb-2"
          >
            ➕ Adicionar Mais Itens
          </a>
          
          {pedido.items?.length > 0 && (
            <small className="text-muted d-block text-center">
              {pedido.items.length} ite{pedido.items.length !== 1 ? 'ns' : 'm'} no carrinho
            </small>
          )}
        </div>
      </div>
    </div>
  );
};

/**
 * Componente individual do item no carrinho
 */
const CartItem = ({ item, onQuantityChange, onRemove, disabled }) => {
  return (
    <div className="cart-item">
      <div className="item-info">
        <div className="item-name">{item.produto?.nome}</div>
        {item.produto?.descricao && (
          <div className="item-description">
            {item.produto.descricao.length > 50 
              ? `${item.produto.descricao.substring(0, 50)}...`
              : item.produto.descricao
            }
          </div>
        )}
      </div>
      
      <div className="item-controls">
        <div className="quantity-control">
          <button
            type="button"
            className="quantity-btn"
            onClick={() => onQuantityChange(item.id, -1)}
            disabled={disabled || item.quantidade <= 1}
          >
            −
          </button>
          
          <input
            type="number"
            className="quantity-input"
            value={item.quantidade}
            min="1"
            readOnly
          />
          
          <button
            type="button"
            className="quantity-btn"
            onClick={() => onQuantityChange(item.id, 1)}
            disabled={disabled}
          >
            +
          </button>
        </div>
        
        <div className="item-price">
          R$ {(item.subtotal || 0).toFixed(2)}
        </div>
        
        <button
          type="button"
          className="remove-btn"
          onClick={() => onRemove(item.id)}
          disabled={disabled}
          title="Remover item"
        >
          🗑️
        </button>
      </div>
    </div>
  );
};

export default OrderSummary;