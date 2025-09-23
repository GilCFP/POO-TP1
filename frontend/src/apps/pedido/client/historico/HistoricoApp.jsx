import React, { useState, useEffect } from 'react';
import { apiService } from '@services/api';
import LoadingSpinner from '@components/common/LoadingSpinner';
import './historico.css';

const HistoricoApp = ({ historicoData, csrfToken }) => {
  const [pedidos, setPedidos] = useState(historicoData?.pedidos || []);
  const [loading, setLoading] = useState(!historicoData?.pedidos);
  const [error, setError] = useState(null);
  const [filtro, setFiltro] = useState('todos');
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);

  // Configurar API service com CSRF token
  useEffect(() => {
    apiService.setCsrfToken(csrfToken);
  }, [csrfToken]);

  // Buscar histórico se não foi fornecido
  useEffect(() => {
    if (!historicoData?.pedidos) {
      fetchHistorico();
    }
  }, []);

  const fetchHistorico = async (pageNum = 1, filtroStatus = 'todos') => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        page: pageNum,
        ...(filtroStatus !== 'todos' && { status: filtroStatus })
      });

      const response = await apiService.get(`/api/pedidos/historico/?${params}`);
      
      if (pageNum === 1) {
        setPedidos(response.data.results);
      } else {
        setPedidos(prev => [...prev, ...response.data.results]);
      }
      
      setHasMore(!!response.data.next);
      setPage(pageNum);
    } catch (err) {
      setError('Erro ao carregar histórico de pedidos');
      console.error('Erro ao buscar histórico:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFiltroChange = (novoFiltro) => {
    setFiltro(novoFiltro);
    setPage(1);
    fetchHistorico(1, novoFiltro);
  };

  const loadMore = () => {
    if (!loading && hasMore) {
      fetchHistorico(page + 1, filtro);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      'pendente': 'status-pending',
      'confirmado': 'status-confirmed',
      'preparando': 'status-preparing',
      'pronto': 'status-ready',
      'entregue': 'status-delivered',
      'cancelado': 'status-cancelled'
    };
    return colors[status] || 'status-default';
  };

  const getStatusText = (status) => {
    const texts = {
      'pendente': 'Pendente',
      'confirmado': 'Confirmado',
      'preparando': 'Preparando',
      'pronto': 'Pronto',
      'entregue': 'Entregue',
      'cancelado': 'Cancelado'
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

  if (loading && pedidos.length === 0) {
    return (
      <div className="historico-container">
        <LoadingSpinner />
        <p>Carregando histórico de pedidos...</p>
      </div>
    );
  }

  if (error && pedidos.length === 0) {
    return (
      <div className="historico-container">
        <div className="error-message">
          <h3>Ops! Algo deu errado</h3>
          <p>{error}</p>
          <button 
            onClick={() => fetchHistorico()}
            className="btn-retry"
          >
            Tentar Novamente
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

      {/* Filtros */}
      <div className="filtros-container">
        <h3>Filtrar por status:</h3>
        <div className="filtros">
          {[
            { key: 'todos', label: 'Todos' },
            { key: 'pendente', label: 'Pendentes' },
            { key: 'confirmado', label: 'Confirmados' },
            { key: 'preparando', label: 'Preparando' },
            { key: 'pronto', label: 'Prontos' },
            { key: 'entregue', label: 'Entregues' },
            { key: 'cancelado', label: 'Cancelados' }
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
      {pedidos.length === 0 ? (
        <div className="no-orders">
          <h3>Nenhum pedido encontrado</h3>
          <p>Você ainda não fez nenhum pedido ou não há pedidos com o filtro selecionado.</p>
        </div>
      ) : (
        <div className="pedidos-list">
          {pedidos.map((pedido) => (
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
                  onClick={() => window.location.href = `/pedidos/${pedido.id}/status/`}
                  className="btn-view-details"
                >
                  Ver Detalhes
                </button>
                
                {pedido.status === 'entregue' && (
                  <button 
                    onClick={() => {/* Implementar recompra */}}
                    className="btn-reorder"
                  >
                    Pedir Novamente
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Botão Carregar Mais */}
      {hasMore && (
        <div className="load-more-container">
          <button 
            onClick={loadMore}
            disabled={loading}
            className="btn-load-more"
          >
            {loading ? <LoadingSpinner size="small" /> : 'Carregar Mais'}
          </button>
        </div>
      )}
    </div>
  );
};

export default HistoricoApp;