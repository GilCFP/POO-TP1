import React, { useEffect } from 'react';
import { useKanbanData } from '../hooks/useKanbanData';
import KanbanColumn from './KanbanColumn';
import LoadingSpinner from '../../../../shared/components/common/LoadingSpinner';
import '../kanban.css';

/**
 * Componente principal do kanban do restaurante
 */
const RestauranteKanban = ({ initialData }) => {
    const {
        ordersByStatus,
        statusChoices,
        loading,
        error,
        refreshOrders,
        advanceOrder,
        updateOrderStatus,
        isOrderUpdating,
        clearError
    } = useKanbanData(initialData);

    // Ordem dos status para exibição no kanban
    const statusOrder = ['2', '3', '4', '5']; // WAITING, PREPARING, READY, BEING_DELIVERED

    /**
     * Manipula o avanço de status de um pedido
     */
    const handleAdvanceStatus = async (orderId) => {
        const success = await advanceOrder(orderId);
        if (!success && error) {
            // Erro já está sendo tratado pelo hook
            console.error('Erro ao avançar status:', error);
        }
    };

    /**
     * Manipula a atualização manual de status
     */
    const handleUpdateStatus = async (orderId, newStatus) => {
        const success = await updateOrderStatus(orderId, newStatus);
        if (!success && error) {
            // Erro já está sendo tratado pelo hook
            console.error('Erro ao atualizar status:', error);
        }
    };

    /**
     * Calcula o total de pedidos em todos os status
     */
    const getTotalOrders = () => {
        return Object.values(ordersByStatus).reduce((total, statusData) => {
            return total + (statusData?.total || 0);
        }, 0);
    };

    /**
     * Atualiza os dados periodicamente (opcional)
     */
    useEffect(() => {
        // Configurar atualização automática a cada 30 segundos
        const interval = setInterval(() => {
            if (!loading) {
                refreshOrders();
            }
        }, 30000);

        return () => clearInterval(interval);
    }, [loading, refreshOrders]);

    return (
        <div className="container-fluid kanban-container">
            {/* Cabeçalho */}
            <div className="row mb-4">
                <div className="col-12">
                    <div className="d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center kanban-header">
                        <div className="mb-2 mb-md-0">
                            <h1 className="h3 mb-2">Kanban - Pedidos do Restaurante</h1>
                            <div className="alert alert-info mb-0">
                                <i className="fas fa-info-circle me-2"></i>
                                <strong>Total de pedidos ativos:</strong> {getTotalOrders()}
                            </div>
                        </div>
                        <div>
                            <button
                                className="btn btn-outline-primary"
                                onClick={refreshOrders}
                                disabled={loading}
                            >
                                {loading ? (
                                    <>
                                        <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                                        Atualizando...
                                    </>
                                ) : (
                                    <>
                                        <i className="fas fa-sync-alt me-2"></i>
                                        Atualizar
                                    </>
                                )}
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            {/* Mensagem de erro */}
            {error && (
                <div className="row mb-3">
                    <div className="col-12">
                        <div className="alert alert-danger alert-dismissible fade show" role="alert">
                            <i className="fas fa-exclamation-triangle me-2"></i>
                            <strong>Erro:</strong> {error}
                            <button 
                                type="button" 
                                className="btn-close" 
                                onClick={clearError}
                                aria-label="Close"
                            ></button>
                        </div>
                    </div>
                </div>
            )}

            {/* Loading overlay para carregamento inicial */}
            {loading && Object.keys(ordersByStatus).length === 0 && (
                <div className="row">
                    <div className="col-12">
                        <LoadingSpinner 
                            size="large" 
                            message="Carregando pedidos..." 
                            center={true}
                        />
                    </div>
                </div>
            )}

            {/* Colunas do kanban */}
            {!loading || Object.keys(ordersByStatus).length > 0 ? (
                <div className="row">
                    {statusOrder.map(statusCode => {
                        const statusData = ordersByStatus[statusCode];
                        
                        return (
                            <KanbanColumn
                                key={statusCode}
                                status={statusCode}
                                statusData={statusData}
                                statusChoices={statusChoices}
                                onAdvanceStatus={handleAdvanceStatus}
                                onUpdateStatus={handleUpdateStatus}
                                isOrderUpdating={isOrderUpdating}
                            />
                        );
                    })}
                </div>
            ) : null}

            {/* Indicador de carregamento global */}
            {loading && Object.keys(ordersByStatus).length > 0 && (
                <div className="loading-toast">
                    <div className="toast show" role="alert">
                        <div className="toast-body d-flex align-items-center">
                            <div className="spinner-border spinner-border-sm me-2" role="status">
                                <span className="visually-hidden">Carregando...</span>
                            </div>
                            Atualizando dados...
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default RestauranteKanban;