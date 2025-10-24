import React, { useState } from 'react';
import LoadingSpinner from '@components/common/LoadingSpinner';
import './historico.css';

const HistoricoApp = ({ historicoData, csrfToken }) => {
  const [pedidos] = useState(historicoData?.pedidos || []);
  const [filtro, setFiltro] = useState('todos');

  // Filtrar pedidos localmente (simplificado para trabalho de POO)
  const pedidosFiltrados = pedidos.filter(pedido => {
    if (filtro === 'todos') return true;
    return pedido.status === filtro;
  });

  const handleFiltroChange = (novoFiltro) => {
    setFiltro(novoFiltro);
  };

  const getStatusColor = (status) => {
    // Mapear status strings do Django para cores
    const colors = {
      'CANCELLED': 'status-cancelled',
      'ORDERING': 'status-ordering',
      'PENDING_PAYMENT': 'status-pending',
      'WAITING': 'status-waiting',
      'PREPARING': 'status-preparing',
      'READY': 'status-ready',
      'DELIVERING': 'status-delivering',
      'DELIVERED': 'status-delivered'
    };
    return colors[status] || 'status-default';
  };

  const getStatusText = (status) => {
    const texts = {
      'CANCELLED': '❌ Cancelado',
      'ORDERING': '📝 Montando',
      'PENDING_PAYMENT': '💳 Aguardando Pagamento',
      'WAITING': '⏳ Confirmado',
      'PREPARING': '👨‍🍳 Preparando',
      'READY': '✅ Pronto',
      'DELIVERING': '🚚 Em Entrega',
      'DELIVERED': '🎉 Entregue'
    };
    return texts[status] || status;
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (!pedidos || pedidos.length === 0) {
    return (
      <div className="historico-container">
        <div className="historico-header">
          <h2>Histórico de Pedidos</h2>
        </div>
        <div className="no-orders">
          <h3>📋 Nenhum pedido encontrado</h3>
          <p>Você ainda não fez nenhum pedido.</p>
          <button 
            onClick={() => window.location.href = '/cardapio/'}
            className="btn-new-order"
          >
            🛒 Fazer Primeiro Pedido
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="historico-container">
      <div className="historico-header">
        <h2>Histórico de Pedidos</h2>
        <p>Acompanhe todos os seus pedidos anteriores</p>
      </div>

      {/* Filtros Simplificados */}
      <div className="filtros-container">
        <h3>Filtrar por status:</h3>
        <div className="filtros">
          {[
            { key: 'todos', label: '📋 Todos' },
            { key: 'DELIVERED', label: '🎉 Entregues' },
            { key: 'PREPARING', label: '👨‍🍳 Preparando' },
            { key: 'CANCELLED', label: '❌ Cancelados' }
          ].map(f => (
            <button
              key={f.key}
              onClick={() => handleFiltroChange(f.key)}
              className={`filtro-btn ${filtro === f.key ? 'active' : ''}`}
            >
              {f.label}
            </button>
          ))}
        </div>
      </div>

      {/* Lista de Pedidos */}
      {pedidosFiltrados.length === 0 ? (
        <div className="no-orders">
          <h3>Nenhum pedido encontrado</h3>
          <p>Não há pedidos com o filtro selecionado.</p>
        </div>
      ) : (
        <div className="pedidos-list">
          {pedidosFiltrados.map((pedido) => (
            <div key={pedido.id} className="pedido-card">
              <div className="pedido-header">
                <div className="pedido-info">
                  <h4>Pedido #{pedido.id}</h4>
                  <p className="pedido-date">{formatDate(pedido.created_at)}</p>
                </div>
                <div className={`status-badge ${getStatusColor(pedido.status)}`}>
                  {getStatusText(pedido.status)}
                </div>
              </div>

              <div className="pedido-content">
                <div className="pedido-items">
                  <h5>Itens do pedido:</h5>
                  {pedido.items?.slice(0, 3).map((item, index) => (
                    <div key={index} className="item-summary">
                      <span>{item.produto?.nome || item.name}</span>
                      <span>x{item.quantity}</span>
                    </div>
                  ))}
                  {pedido.items?.length > 3 && (
                    <p className="items-more">
                      +{pedido.items.length - 3} itens adicionais
                    </p>
                  )}
                </div>

                <div className="pedido-total">
                  <strong>Total: R$ {pedido.total_price?.toFixed(2)}</strong>
                </div>
              </div>

              <div className="pedido-actions">
                <button 
                  onClick={() => window.location.href = `/pedido/${pedido.id}/status/`}
                  className="btn-view-details"
                >
                  👁️ Ver Detalhes
                </button>
                
                {pedido.status === 'DELIVERED' && (
                  <button 
                    onClick={() => {
                      alert('Função "Pedir Novamente" - Simulação para trabalho de POO!\n\nEm um sistema real, isso adicionaria todos os itens ao carrinho.');
                    }}
                    className="btn-reorder"
                  >
                    🔄 Pedir Novamente
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Informações adicionais */}
      <div className="historico-footer">
        <p>Mostrando {pedidosFiltrados.length} de {pedidos.length} pedidos</p>
        <button 
          onClick={() => window.location.href = '/cardapio/'}
          className="btn-new-order-footer"
        >
          🛒 Fazer Novo Pedido
        </button>
      </div>
    </div>
  );
};

export default HistoricoApp;