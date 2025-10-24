import React, { useState, useEffect } from 'react';
import { pedidoService } from '@pedido/shared/services/pedidoService';
import LoadingSpinner from '@components/common/LoadingSpinner';
import './status.css';

const StatusApp = ({ statusData, csrfToken }) => {
  const [pedido, setPedido] = useState(statusData?.pedido || null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Auto-refresh a cada 30 segundos para atualizações em tempo real (simplificado)
  useEffect(() => {
    if (pedido && pedido.id) {
      const interval = setInterval(() => {
        // Para trabalho de POO, apenas simula refresh
        console.log('Simulando refresh do status...');
      }, 30000); // 30 segundos

      return () => clearInterval(interval);
    }
  }, [pedido]);

  const fetchPedidoStatus = async (pedidoId) => {
    try {
      setLoading(true);
      // Para trabalho de POO, apenas simula carregamento
      await new Promise(resolve => setTimeout(resolve, 1000));
      console.log('Status atualizado (simulado)');
      setError(null);
    } catch (err) {
      setError('Erro ao carregar status do pedido');
      console.error('Erro ao buscar pedido:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    // Mapear status strings para cores (baseado no StatusPedido do Django)
    const colors = {
      '-1': 'status-cancelled',   // Cancelado
      '0': 'status-ordering',     // Fazendo pedido
      '1': 'status-pending',      // Aguardando pagamento
      '2': 'status-waiting',      // Aguardando
      '3': 'status-preparing',    // Preparando
      '4': 'status-ready',        // Pronto
      '5': 'status-delivering',   // Sendo entregue
      '6': 'status-delivered'     // Entregue
    };
    return colors[String(status)] || 'status-default';
    return colors[status] || 'status-default';
  };

  const getStatusText = (status) => {
    const texts = {
      '-1': '❌ Pedido Cancelado',
      '0': '📝 Montando Pedido',
      '1': '💳 Aguardando Pagamento',
      '2': '⏳ Pedido Confirmado',
      '3': '👨‍🍳 Preparando seu Pedido',
      '4': '✅ Pedido Pronto!',
      '5': '🚚 Saiu para Entrega',
      '6': '🎉 Pedido Entregue'
    };
    return texts[status] || '❓ Status Desconhecido';
  };

  if (loading) {
    return (
      <div className="status-container">
        <LoadingSpinner />
        <p>Carregando status do pedido...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="status-container">
        <div className="error-message">
          <h3>Ops! Algo deu errado</h3>
          <p>{error}</p>
          <button 
            onClick={() => window.location.reload()}
            className="btn-retry"
          >
            Tentar Novamente
          </button>
        </div>
      </div>
    );
  }

  if (!pedido) {
    return (
      <div className="status-container">
        <div className="no-order">
          <h3>Pedido não encontrado</h3>
          <p>Não foi possível encontrar o pedido solicitado.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="status-container">
      <div className="status-header">
        <h2>Status do Pedido #{pedido.id}</h2>
        <p className="order-date">
          {pedido.created_at ? (
            `Pedido realizado em: ${new Date(pedido.created_at).toLocaleString('pt-BR')}`
          ) : (
            'Data do pedido não disponível'
          )}
        </p>
      </div>

      <div className="status-progress">
        <div className={`status-badge ${getStatusColor(pedido.status)}`}>
          <span className="status-text">{getStatusText(pedido.status)}</span>
        </div>
        
        {pedido.estimated_delivery && (
          <div className="delivery-estimate">
            <p>Previsão de entrega: {new Date(pedido.estimated_delivery).toLocaleString('pt-BR')}</p>
          </div>
        )}
      </div>

      <div className="order-details">
        <h3>Detalhes do Pedido</h3>
        <div className="order-items">
          {pedido.items?.length > 0 ? (
            pedido.items.map((item, index) => (
              <div key={index} className="order-item">
                <span className="item-name">{item.produto?.nome || 'Produto'}</span>
                <span className="item-quantity">x{item.quantity || 1}</span>
                <span className="item-price">R$ {(item.price || 0).toFixed(2)}</span>
              </div>
            ))
          ) : (
            <p>Nenhum item encontrado</p>
          )}
        </div>
        
        <div className="order-total">
          <strong>Total: R$ {(pedido.total_price || 0).toFixed(2)}</strong>
        </div>
      </div>

      {pedido.delivery_address && (
        <div className="delivery-info">
          <h3>Endereço de Entrega</h3>
          <p>{pedido.delivery_address}</p>
        </div>
      )}

      <div className="status-actions">
        <button 
          onClick={() => fetchPedidoStatus(pedido.id)}
          className="btn-refresh"
          disabled={loading}
        >
          {loading ? '🔄 Atualizando...' : '🔄 Atualizar Status'}
        </button>
        
        <button 
          onClick={() => window.location.href = '/produtos/'}
          className="btn-new-order"
        >
          🛒 Fazer Novo Pedido
        </button>
        
        {(pedido.status === 'ORDERING' || pedido.status === 'PENDING_PAYMENT') && (
          <button 
            onClick={() => {
              if (confirm('Tem certeza que deseja cancelar este pedido?')) {
                alert('Pedido cancelado! (simulação para trabalho de POO)');
              }
            }}
            className="btn-cancel"
          >
            ❌ Cancelar Pedido
          </button>
        )}
      </div>
    </div>
  );
};

export default StatusApp;