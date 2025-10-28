import React from 'react';

/**
 * Componente para exibir um cartão de pedido no kanban
 */
const OrderCard = ({ 
    order, 
    statusChoices, 
    onAdvanceStatus, 
    onUpdateStatus, 
    isUpdating = false,
    canAdvance = true 
}) => {
    /**
     * Formata preço para o padrão brasileiro
     */
    const formatPrice = (price) => {
        return `R$ ${price.toFixed(2).replace('.', ',')}`;
    };

    /**
     * Formata data para o padrão brasileiro
     */
    const formatDate = (isoString) => {
        const date = new Date(isoString);
        return date.toLocaleString('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    /**
     * Manipula o clique no botão avançar
     */
    const handleAdvance = () => {
        if (!isUpdating && onAdvanceStatus) {
            onAdvanceStatus(order.id);
        }
    };

    /**
     * Manipula a mudança de status manual
     */
    const handleStatusChange = (newStatus) => {
        if (!isUpdating && onUpdateStatus && newStatus !== order.status) {
            onUpdateStatus(order.id, newStatus);
        }
    };

    /**
     * Retorna a classe CSS baseada no status
     */
    const getStatusClass = (status) => {
        const statusClasses = {
            '2': 'waiting',
            '3': 'preparing', 
            '4': 'ready',
            '5': 'delivering'
        };
        return statusClasses[status] || 'default';
    };

    return (
        <div className={`card mb-2 border-light order-card ${isUpdating ? 'updating' : ''} status-${getStatusClass(order.status)}`}>
            <div className="card-body p-2">
                {/* Cabeçalho com ID e preço */}
                <div className="d-flex justify-content-between align-items-start mb-2">
                    <small className="text-muted">#{order.id}</small>
                    <strong className="text-success">
                        {formatPrice(order.total)}
                    </strong>
                </div>
                
                {/* Informações do cliente */}
                <div className="mb-2">
                    <strong>{order.cliente.nome}</strong>
                    <br />
                    <small className="text-muted">
                        <i className="fas fa-phone status-icon"></i>{order.cliente.telefone}
                    </small>
                </div>

                {/* Data de criação */}
                <div className="mb-2">
                    <small className="text-muted">
                        <i className="fas fa-clock status-icon"></i>{formatDate(order.criado_em)}
                    </small>
                </div>

                {/* Endereço de entrega */}
                {order.endereco_entrega && (
                    <div className="mb-2">
                        <small className="text-muted">
                            <i className="fas fa-map-marker-alt status-icon"></i>{order.endereco_entrega}
                        </small>
                    </div>
                )}

                {/* Lista de itens */}
                <div className="mb-2">
                    <small><strong>Itens:</strong></small>
                    {order.items && order.items.map(item => (
                        <div key={item.id}>
                            <small className="text-muted">
                                {item.quantidade}x {item.produto_nome}
                            </small>
                        </div>
                    ))}
                </div>

                {/* Observações especiais */}
                {order.observacoes && (
                    <div className="mb-2">
                        <small>
                            <strong>Obs:</strong> {order.observacoes}
                        </small>
                    </div>
                )}

                {/* Botões de ação */}
                <div className="btn-group w-100" role="group">
                    {/* Botão Avançar */}
                    {canAdvance && (
                        <button
                            className="btn btn-sm btn-outline-primary"
                            onClick={handleAdvance}
                            disabled={isUpdating}
                        >
                            {isUpdating ? (
                                <>
                                    <span className="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
                                    Processando...
                                </>
                            ) : (
                                'Avançar'
                            )}
                        </button>
                    )}
                    
                    {/* Dropdown de status */}
                    <div className="dropdown">
                        <button
                            className="btn btn-sm btn-outline-secondary dropdown-toggle"
                            type="button"
                            data-bs-toggle="dropdown"
                            disabled={isUpdating}
                            aria-expanded="false"
                        >
                            Status
                        </button>
                        <ul className="dropdown-menu">
                            {statusChoices.map(status => (
                                <li key={status.codigo}>
                                    <button
                                        className={`dropdown-item ${status.codigo === order.status ? 'active' : ''}`}
                                        onClick={() => handleStatusChange(status.codigo)}
                                        disabled={status.codigo === order.status || isUpdating}
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
    );
};

export default OrderCard;