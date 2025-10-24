import React, { useState, useEffect } from 'react';
import { getCsrfToken } from '../../../../shared/utils/csrf';

const AdminDashboard = ({ initialData }) => {
    const [pedidosPorStatus, setPedidosPorStatus] = useState(initialData.pedidos_por_status);
    const [statusChoices] = useState(initialData.status_choices);
    const [loading, setLoading] = useState(false);

    const statusOrder = [0, 1, 2, 3, 4, 5]; // ORDERING, PENDING_PAYMENT, PAID, PREPARING, READY, DELIVERED

    const getStatusColor = (statusCode) => {
        const colors = {
            0: 'secondary',  // ORDERING
            1: 'warning',    // PENDING_PAYMENT
            2: 'info',       // PAID
            3: 'primary',    // PREPARING
            4: 'success',    // READY
            5: 'dark'        // DELIVERED
        };
        return colors[statusCode] || 'secondary';
    };

    const atualizarStatusPedido = async (pedidoId, novoStatus) => {
        setLoading(true);
        try {
            const response = await fetch(`/api/pedidos/_pedido/${pedidoId}/atualizar-status/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify({ status: novoStatus })
            });
            
            if (response.ok) {
                // Recarregar dados
                window.location.reload();
            } else {
                alert('Erro ao atualizar status do pedido');
            }
        } catch (error) {
            console.error('Erro:', error);
            alert('Erro ao atualizar status do pedido');
        } finally {
            setLoading(false);
        }
    };

    const avancarStatus = async (pedidoId) => {
        setLoading(true);
        try {
            const response = await fetch(`/api/pedidos/_pedido/${pedidoId}/avancar-status/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                }
            });
            
            if (response.ok) {
                // Recarregar dados
                window.location.reload();
            } else {
                alert('Erro ao avançar status do pedido');
            }
        } catch (error) {
            console.error('Erro:', error);
            alert('Erro ao avançar status do pedido');
        } finally {
            setLoading(false);
        }
    };

    const formatarData = (isoString) => {
        const data = new Date(isoString);
        return data.toLocaleString('pt-BR');
    };

    const formatarPreco = (preco) => {
        return `R$ ${preco.toFixed(2).replace('.', ',')}`;
    };

    return (
        <div className="container-fluid">
            <div className="row mb-4">
                <div className="col-12">
                    <h1 className="h3 mb-3">Painel Administrativo - Pedidos</h1>
                    <div className="alert alert-info">
                        <strong>Total de pedidos:</strong> {initialData.total_pedidos}
                    </div>
                </div>
            </div>

            <div className="row">
                {statusOrder.map(statusCode => {
                    const statusData = pedidosPorStatus[statusCode];
                    if (!statusData) return null;

                    return (
                        <div key={statusCode} className="col-lg-2 col-md-4 col-sm-6 mb-4">
                            <div className={`card border-${getStatusColor(statusCode)}`}>
                                <div className={`card-header bg-${getStatusColor(statusCode)} text-white`}>
                                    <h6 className="card-title mb-0">
                                        {statusData.nome}
                                        <span className="badge badge-light ms-2">
                                            {statusData.total}
                                        </span>
                                    </h6>
                                </div>
                                <div className="card-body p-2" style={{ maxHeight: '600px', overflowY: 'auto' }}>
                                    {statusData.pedidos.length === 0 ? (
                                        <p className="text-muted text-center">Nenhum pedido</p>
                                    ) : (
                                        statusData.pedidos.map(pedido => (
                                            <div key={pedido.id} className="card mb-2 border-light">
                                                <div className="card-body p-2">
                                                    <div className="d-flex justify-content-between align-items-start mb-2">
                                                        <small className="text-muted">#{pedido.id}</small>
                                                        <strong className="text-success">
                                                            {formatarPreco(pedido.total)}
                                                        </strong>
                                                    </div>
                                                    
                                                    <div className="mb-2">
                                                        <strong>{pedido.cliente.nome}</strong>
                                                        <br />
                                                        <small className="text-muted">
                                                            {pedido.cliente.telefone}
                                                        </small>
                                                    </div>

                                                    <div className="mb-2">
                                                        <small className="text-muted">
                                                            {formatarData(pedido.criado_em)}
                                                        </small>
                                                    </div>

                                                    {pedido.endereco_entrega && (
                                                        <div className="mb-2">
                                                            <small className="text-muted">
                                                                <i className="fas fa-map-marker-alt"></i>
                                                                {' ' + pedido.endereco_entrega}
                                                            </small>
                                                        </div>
                                                    )}

                                                    <div className="mb-2">
                                                        <small><strong>Itens:</strong></small>
                                                        {pedido.items.map(item => (
                                                            <div key={item.id}>
                                                                <small className="text-muted">
                                                                    {item.quantidade}x {item.produto_nome}
                                                                </small>
                                                            </div>
                                                        ))}
                                                    </div>

                                                    {pedido.observacoes && (
                                                        <div className="mb-2">
                                                            <small>
                                                                <strong>Obs:</strong> {pedido.observacoes}
                                                            </small>
                                                        </div>
                                                    )}

                                                    {/* Botões de ação */}
                                                    <div className="btn-group w-100" role="group">
                                                        {statusCode < 5 && (
                                                            <button
                                                                className="btn btn-sm btn-outline-primary"
                                                                onClick={() => avancarStatus(pedido.id)}
                                                                disabled={loading}
                                                            >
                                                                Avançar
                                                            </button>
                                                        )}
                                                        
                                                        <div className="dropdown">
                                                            <button
                                                                className="btn btn-sm btn-outline-secondary dropdown-toggle"
                                                                type="button"
                                                                data-bs-toggle="dropdown"
                                                                disabled={loading}
                                                            >
                                                                Status
                                                            </button>
                                                            <ul className="dropdown-menu">
                                                                {statusChoices.map(status => (
                                                                    <li key={status.codigo}>
                                                                        <button
                                                                            className="dropdown-item"
                                                                            onClick={() => atualizarStatusPedido(pedido.id, status.codigo)}
                                                                            disabled={status.codigo === statusCode}
                                                                        >
                                                                            {status.nome}
                                                                        </button>
                                                                    </li>
                                                                ))}
                                                            </ul>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        ))
                                    )}
                                </div>
                            </div>
                        </div>
                    );
                })}
            </div>

            {loading && (
                <div className="position-fixed top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center" 
                     style={{ backgroundColor: 'rgba(0,0,0,0.3)', zIndex: 9999 }}>
                    <div className="spinner-border text-primary" role="status">
                        <span className="visually-hidden">Carregando...</span>
                    </div>
                </div>
            )}
        </div>
    );
};

export default AdminDashboard;