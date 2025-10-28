import React from 'react';
import OrderCard from './OrderCard';

/**
 * Componente para uma coluna do kanban representando um status
 */
const KanbanColumn = ({ 
    status, 
    statusData, 
    statusChoices, 
    onAdvanceStatus, 
    onUpdateStatus, 
    isOrderUpdating 
}) => {
    /**
     * Determina a cor da coluna baseada no status
     */
    const getStatusColor = (statusCode) => {
        const statusInfo = {
            '2': { color: 'warning', icon: 'fas fa-hourglass-half' }, // WAITING
            '3': { color: 'primary', icon: 'fas fa-fire-alt' },       // PREPARING
            '4': { color: 'success', icon: 'fas fa-check-circle' },   // READY
            '5': { color: 'info', icon: 'fas fa-truck' }              // BEING_DELIVERED
        };
        return statusInfo[statusCode] || { color: 'secondary', icon: 'fas fa-question-circle' };
    };

    /**
     * Retorna a classe de cor para o gradiente do cabeçalho
     */
    const getHeaderGradientClass = (color) => {
        const gradients = {
            'warning': 'kanban-header-warning', 'primary': 'kanban-header-primary',
            'success': 'kanban-header-success', 'info': 'kanban-header-info',
        };
        return gradients[color] || 'kanban-header-secondary';
    };

    /**
     * Verifica se um pedido pode avançar para o próximo status
     */
    const canAdvanceOrder = (order) => {
        // Pedidos "Sendo Entregue" não podem avançar mais
        return status !== '5';
    };

    if (!statusData) {
        return null;
    }

    const { color, icon } = getStatusColor(status);
    const headerGradientClass = getHeaderGradientClass(color);

    return (
        <div className="col-lg-3 col-md-6 col-sm-12 mb-4 kanban-column">
            <div className="card kanban-column-card">
                {/* Cabeçalho da coluna */}
                <div className={`card-header text-white ${headerGradientClass}`}>
                    <h6 className="card-title mb-0 d-flex justify-content-between align-items-center">
                        <div className="d-flex align-items-center">
                            <i className={`${icon} me-2`}></i>
                            <span>{statusData.name}</span>
                        </div>
                        <span className="badge bg-light text-dark rounded-pill">
                            {statusData.total || 0}
                        </span>
                    </h6>
                </div>

                {/* Corpo da coluna com lista de pedidos */}
                <div 
                    className="card-body p-2" 
                    style={{ 
                        maxHeight: '600px', 
                        overflowY: 'auto',
                        minHeight: '200px'
                    }}
                >
                    {!statusData.orders || statusData.orders.length === 0 ? (
                        <div className="empty-state">
                            <i className="fas fa-inbox fa-2x"></i>
                            <p className="mb-0">Nenhum pedido</p>
                        </div>
                    ) : (
                        statusData.orders.map(order => (
                            <OrderCard
                                key={order.id}
                                order={order}
                                statusChoices={statusChoices}
                                onAdvanceStatus={onAdvanceStatus}
                                onUpdateStatus={onUpdateStatus}
                                isUpdating={isOrderUpdating(order.id)}
                                canAdvance={canAdvanceOrder(order)}
                            />
                        ))
                    )}
                </div>
            </div>
        </div>
    );
};

export default KanbanColumn;