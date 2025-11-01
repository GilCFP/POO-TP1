/**
 * index.js - Entry point para o dashboard do restaurante
 */

import React from 'react';
import { createRoot } from 'react-dom/client';
import RestauranteDashboard from './RestauranteDashboard';

// Estilo adicional para componentes específicos
const additionalStyles = `
/* Estilos específicos para componentes React do Dashboard */

/* Loading states */
.chart-loading, .products-loading {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 200px;
    color: #6c757d;
}

.chart-skeleton {
    width: 100%;
    height: 100%;
    background: #f8f9fa;
    border-radius: 4px;
    position: relative;
    overflow: hidden;
}

.skeleton-bars {
    display: flex;
    align-items: end;
    justify-content: space-around;
    height: 100%;
    padding: 20px;
}

.skeleton-bar {
    width: 20px;
    background: linear-gradient(90deg, #e9ecef 25%, #f8f9fa 50%, #e9ecef 75%);
    background-size: 200% 100%;
    animation: skeleton-loading 1.5s infinite;
    border-radius: 2px;
}

@keyframes skeleton-loading {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}

/* Métricas */
.metric-skeleton {
    height: 40px;
    background: linear-gradient(90deg, #e9ecef 25%, #f8f9fa 50%, #e9ecef 75%);
    background-size: 200% 100%;
    animation: skeleton-loading 1.5s infinite;
    border-radius: 4px;
}

.metrics-summary {
    margin-top: 20px;
    padding: 16px;
    background: #f8f9fa;
    border-radius: 8px;
    display: flex;
    gap: 20px;
    flex-wrap: wrap;
    font-size: 0.9rem;
}

.summary-item {
    color: #6c757d;
}

.metrics-empty {
    text-align: center;
    padding: 40px;
    color: #6c757d;
}

.metrics-empty .empty-icon {
    font-size: 3rem;
    margin-bottom: 16px;
}

/* Filtros de período */
.dashboard-controls {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    background: white;
    padding: 16px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.08);
}

.dashboard-status {
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 0.85rem;
    color: #6c757d;
}

.btn-refresh {
    background: white;
    border: 1px solid #dee2e6;
    border-radius: 4px;
    padding: 6px 8px;
    cursor: pointer;
    transition: all 0.3s;
}

.btn-refresh:hover {
    border-color: #667eea;
    color: #667eea;
}

.btn-refresh:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

/* Filtros customizados */
.custom-date-picker {
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 6px;
    padding: 16px;
    margin-top: 12px;
}

.date-inputs {
    display: flex;
    gap: 16px;
    margin-bottom: 12px;
}

.date-input-group {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.date-input-group label {
    font-size: 0.85rem;
    font-weight: 500;
    color: #495057;
}

.date-input-group input {
    padding: 6px 8px;
    border: 1px solid #ced4da;
    border-radius: 4px;
    font-size: 0.9rem;
}

.date-actions {
    display: flex;
    gap: 8px;
}

.btn-sm {
    padding: 4px 12px;
    font-size: 0.8rem;
}

.date-error {
    color: #dc3545;
    margin-top: 8px;
}

.active-period-indicator {
    margin-top: 8px;
    color: #6c757d;
}

/* Charts */
.chart-stats {
    display: flex;
    gap: 16px;
    font-size: 0.85rem;
}

.stat-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
}

.stat-value {
    font-weight: 600;
    color: #343a40;
}

.stat-label {
    color: #6c757d;
    font-size: 0.75rem;
}

.chart-empty {
    text-align: center;
    padding: 40px;
    color: #6c757d;
}

.chart-empty .empty-icon {
    font-size: 2.5rem;
    margin-bottom: 12px;
}

.chart-insights {
    margin-top: 16px;
    padding: 12px;
    background: #f8f9fa;
    border-radius: 6px;
    font-size: 0.9rem;
    color: #495057;
}

/* Products */
.products-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
}

.sort-select {
    padding: 4px 8px;
    border: 1px solid #ced4da;
    border-radius: 4px;
    font-size: 0.8rem;
    background: white;
}

.product-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 0;
    border-bottom: 1px solid #f1f3f4;
}

.product-item:last-child {
    border-bottom: none;
}

.product-rank {
    font-weight: 600;
    color: #667eea;
    min-width: 24px;
}

.product-info {
    flex: 1;
}

.product-name {
    font-weight: 500;
    color: #343a40;
    margin-bottom: 4px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.product-metrics {
    display: flex;
    gap: 12px;
    font-size: 0.8rem;
    color: #6c757d;
    margin-bottom: 6px;
}

.product-bar {
    height: 4px;
    background: #e9ecef;
    border-radius: 2px;
    overflow: hidden;
}

.product-bar-fill {
    height: 100%;
    background: linear-gradient(90deg, #667eea, #764ba2);
    border-radius: 2px;
    transition: width 0.3s ease;
}

.products-empty {
    text-align: center;
    padding: 40px;
    color: #6c757d;
}

.products-empty .empty-icon {
    font-size: 2.5rem;
    margin-bottom: 12px;
}

.products-summary {
    margin-top: 16px;
    padding: 12px;
    background: #f8f9fa;
    border-radius: 6px;
    font-size: 0.85rem;
}

.summary-stats {
    display: flex;
    flex-direction: column;
    gap: 4px;
    margin-bottom: 8px;
}

.top-insights {
    color: #495057;
    font-style: italic;
}

/* Skeleton loading para produtos */
.product-item.skeleton .product-rank,
.product-item.skeleton .product-name,
.product-item.skeleton .skeleton-text,
.product-item.skeleton .skeleton-bar {
    background: linear-gradient(90deg, #e9ecef 25%, #f8f9fa 50%, #e9ecef 75%);
    background-size: 200% 100%;
    animation: skeleton-loading 1.5s infinite;
    border-radius: 4px;
}

.skeleton-text {
    height: 16px;
    margin: 2px 0;
}

.skeleton-text.short {
    width: 60%;
}

.skeleton-bar {
    height: 4px;
    width: 100%;
}

/* Alerts */
.alert {
    padding: 12px 16px;
    border-radius: 6px;
    margin-bottom: 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.alert-warning {
    background: #fff3cd;
    border: 1px solid #ffeaa7;
    color: #856404;
}

.dashboard-footer {
    margin-top: 24px;
    text-align: center;
    color: #6c757d;
    font-size: 0.85rem;
    padding: 16px;
    background: #f8f9fa;
    border-radius: 6px;
}

/* Responsividade */
@media (max-width: 768px) {
    .dashboard-controls {
        flex-direction: column;
        gap: 12px;
    }
    
    .date-inputs {
        flex-direction: column;
    }
    
    .chart-stats {
        justify-content: center;
    }
    
    .products-header {
        flex-direction: column;
        gap: 8px;
    }
    
    .product-metrics {
        flex-direction: column;
        gap: 4px;
    }
    
    .summary-stats {
        gap: 8px;
    }
}
`;

// Inicialização do dashboard
document.addEventListener('DOMContentLoaded', function() {
    // Adicionar estilos CSS
    const style = document.createElement('style');
    style.textContent = additionalStyles;
    document.head.appendChild(style);
    
    // Encontrar container do dashboard
    const container = document.getElementById('dashboard-root');
    
    if (container) {
        try {
            // Verificar se a configuração está disponível
            if (!window.DASHBOARD_CONFIG) {
                throw new Error('Configuração do dashboard não encontrada');
            }
            
            // Criar root do React
            const root = createRoot(container);
            
            // Renderizar componente principal
            root.render(<RestauranteDashboard />);
            
            console.log('Dashboard do restaurante carregado com sucesso');
            
        } catch (error) {
            console.error('Erro ao inicializar dashboard:', error);
            
            // Fallback para erro
            container.innerHTML = `
                <div class="dashboard-error">
                    <h3>Erro ao Carregar Dashboard</h3>
                    <p>${error.message}</p>
                    <button onclick="window.location.reload()" class="btn btn-primary">
                        Recarregar Página
                    </button>
                </div>
            `;
        }
    } else {
        console.warn('Container do dashboard (#dashboard-root) não encontrado');
    }
});

// Exportar para possível uso externo
export default RestauranteDashboard;