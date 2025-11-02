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

  // Se está carregando, não mostrar
  if (loading) {
    return null;
  }

  // Se não há pedido ativo, não mostrar
  if (!pedidoAtivo) {
    return null;
  }

  // Tentar acessar os dados do pedido de diferentes formas
  const pedido = pedidoAtivo.pedido || pedidoAtivo;
  const items = pedido?.items || pedido?.itens || [];
  const totalItens = items.reduce((total, item) => total + (item.quantidade || 0), 0);
  const totalValor = pedido?.total_price || pedido?.total || 0;

  // Se não há itens, não mostrar
  if (totalItens === 0) {
    return null;
  }

  const handleClick = () => {
    onViewCarrinho(pedidoAtivo);
  };

  return (
    <div className={`carrinho-indicador ${className}`} style={{
      position: 'fixed',
      bottom: '30px',
      left: '50%',
      transform: 'translateX(-50%)',
      zIndex: 1000
    }}>
      <button 
        className="carrinho-indicador-button"
        onClick={handleClick}
        type="button"
        style={{
          backgroundColor: '#ff6b35',
          color: 'white',
          border: 'none',
          borderRadius: '25px',
          padding: '20px 40px',
          display: 'flex',
          alignItems: 'center',
          gap: '15px',
          cursor: 'pointer',
          fontSize: '18px',
          fontWeight: 'bold',
          boxShadow: '0 8px 24px rgba(0,0,0,0.2)',
          transition: 'all 0.3s ease',
          minWidth: '280px',
          justifyContent: 'center'
        }}
        onMouseOver={(e) => {
          e.target.style.backgroundColor = '#e55a2e';
          e.target.style.transform = 'scale(1.05)';
        }}
        onMouseOut={(e) => {
          e.target.style.backgroundColor = '#ff6b35';
          e.target.style.transform = 'scale(1)';
        }}
      >
        <div className="carrinho-icon" style={{ fontSize: '22px' }}>
          <i className="fas fa-shopping-cart"></i>
          {showItemCount && totalItens > 0 && (
            <span className="item-count" style={{
              backgroundColor: '#fff',
              color: '#ff6b35',
              borderRadius: '50%',
              minWidth: '24px',
              height: '24px',
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '14px',
              fontWeight: 'bold',
              marginLeft: '8px'
            }}>{totalItens}</span>
          )}
        </div>
        
        <div className="carrinho-info">
          <span className="carrinho-label" style={{ fontSize: '16px' }}>Meu Pedido</span>
          {showTotal && (
            <span className="carrinho-total" style={{ 
              marginLeft: '15px', 
              fontSize: '18px',
              fontWeight: 'bold'
            }}>
              R$ {totalValor.toFixed(2)}
            </span>
          )}
        </div>
        
        <div className="carrinho-arrow" style={{ fontSize: '18px' }}>
          <i className="fas fa-chevron-right"></i>
        </div>
      </button>
    </div>
  );
};

export default CarrinhoIndicador;