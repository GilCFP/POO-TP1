import React from 'react';
import { useCarrinho } from '@pedido/shared/hooks/useCarrinho';
import './CarrinhoIndicador.css';

/**
 * Componente que mostra um indicador do carrinho/pedido ativo
 */
const CarrinhoIndicador = ({ 
  showTotal = true, 
  showItemCount = true,
  onViewCarrinho = () => {},
  className = ''
}) => {
  const { pedidoAtivo, loading } = useCarrinho();

  // Se não há pedido ativo ou está carregando, não mostrar
  if (!pedidoAtivo || loading) {
    return null;
  }

  const { pedido } = pedidoAtivo;
  const items = pedido?.itens || [];
  const totalItens = items.reduce((total, item) => total + (item.quantidade || 0), 0);
  const totalValor = pedido?.total || 0;

  // Se não há itens, não mostrar
  if (totalItens === 0) {
    return null;
  }

  const handleClick = () => {
    onViewCarrinho(pedidoAtivo);
  };

  return (
    <div className={`carrinho-indicador ${className}`}>
      <button 
        className="carrinho-indicador-button"
        onClick={handleClick}
        type="button"
      >
        <div className="carrinho-icon">
          <i className="fas fa-shopping-cart"></i>
          {showItemCount && totalItens > 0 && (
            <span className="item-count">{totalItens}</span>
          )}
        </div>
        
        <div className="carrinho-info">
          <span className="carrinho-label">Meu Pedido</span>
          {showTotal && (
            <span className="carrinho-total">R$ {totalValor.toFixed(2)}</span>
          )}
        </div>
        
        <div className="carrinho-arrow">
          <i className="fas fa-chevron-right"></i>
        </div>
      </button>
    </div>
  );
};

export default CarrinhoIndicador;