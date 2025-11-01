/**
 * DashboardMetrics - Componente para exibir métricas principais do dashboard
 */

import React from 'react';
import DashboardService from '../services/dashboardService';

const DashboardMetrics = ({ metrics, loading, period }) => {
    // Fallback para dados vazios
    const defaultMetrics = {
        sales_metrics: {
            total_sales: 0,
            total_orders: 0,
            average_ticket: 0
        },
        avg_order_time: 0,
        returned_orders_metrics: {
            returned_orders_count: 0,
            returned_orders_value: 0
        }
    };
    
    const data = metrics || defaultMetrics;
    const salesMetrics = data.sales_metrics || defaultMetrics.sales_metrics;
    const returnedMetrics = data.returned_orders_metrics || defaultMetrics.returned_orders_metrics;
    
    // Componente de card de métrica
    const MetricCard = ({ title, value, format = 'number', change = null, icon = '', loading: cardLoading = false }) => (
        <div className="metric-card">
            <h3>
                {icon && <span className="metric-icon">{icon}</span>}
                {title}
            </h3>
            
            {cardLoading ? (
                <div className="metric-loading">
                    <div className="metric-skeleton"></div>
                </div>
            ) : (
                <>
                    <div className="metric-value">
                        {format === 'currency' ? DashboardService.formatCurrency(value) : 
                         format === 'percentage' ? `${value}%` :
                         format === 'time' ? `${value} min` :
                         typeof value === 'number' ? value.toLocaleString('pt-BR') : value}
                    </div>
                    
                    {change && (
                        <div className={`metric-change ${change.direction}`}>
                            <span className="icon">
                                {change.direction === 'positive' ? '↗' : 
                                 change.direction === 'negative' ? '↘' : '→'}
                            </span>
                            {change.isValid ? `${change.percentage}%` : 'N/A'}
                            <span className="change-label">vs período anterior</span>
                        </div>
                    )}
                </>
            )}
        </div>
    );
    
    // Calcular taxa de retorno
    const returnRate = salesMetrics.total_orders > 0 
        ? ((returnedMetrics.returned_orders_count / salesMetrics.total_orders) * 100).toFixed(1)
        : 0;
    
    return (
        <div className="dashboard-metrics">
            <div className="metrics-grid">
                {/* Vendas Totais */}
                <MetricCard
                    title="Vendas Totais"
                    value={salesMetrics.total_sales}
                    format="currency"
                    icon="💰"
                    loading={loading}
                />
                
                {/* Total de Pedidos */}
                <MetricCard
                    title="Total de Pedidos"
                    value={salesMetrics.total_orders}
                    format="number"
                    icon="📦"
                    loading={loading}
                />
                
                {/* Ticket Médio */}
                <MetricCard
                    title="Ticket Médio"
                    value={salesMetrics.average_ticket}
                    format="currency"
                    icon="🎯"
                    loading={loading}
                />
                
                {/* Tempo Médio de Preparo */}
                <MetricCard
                    title="Tempo Médio de Preparo"
                    value={data.avg_order_time || 0}
                    format="time"
                    icon="⏱️"
                    loading={loading}
                />
                
                {/* Pedidos Cancelados */}
                <MetricCard
                    title="Pedidos Cancelados"
                    value={returnedMetrics.returned_orders_count}
                    format="number"
                    icon="❌"
                    loading={loading}
                />
                
                {/* Taxa de Cancelamento */}
                <MetricCard
                    title="Taxa de Cancelamento"
                    value={returnRate}
                    format="percentage"
                    icon="📊"
                    loading={loading}
                />
            </div>
            
            {/* Informações adicionais */}
            {!loading && (
                <div className="metrics-summary">
                    <div className="summary-item">
                        <strong>Período:</strong> {period?.days || 0} dias
                    </div>
                    
                    {salesMetrics.total_orders > 0 && (
                        <>
                            <div className="summary-item">
                                <strong>Pedidos por dia:</strong> {(salesMetrics.total_orders / (period?.days || 1)).toFixed(1)}
                            </div>
                            
                            <div className="summary-item">
                                <strong>Vendas por dia:</strong> {DashboardService.formatCurrency(salesMetrics.total_sales / (period?.days || 1))}
                            </div>
                        </>
                    )}
                </div>
            )}
            
            {/* Estado vazio */}
            {!loading && salesMetrics.total_orders === 0 && (
                <div className="metrics-empty">
                    <div className="empty-icon">📊</div>
                    <h4>Nenhuma venda encontrada</h4>
                    <p>Não há dados de vendas para o período selecionado.</p>
                    <small>Tente selecionar um período diferente ou verifique se há pedidos finalizados.</small>
                </div>
            )}
        </div>
    );
};

export default DashboardMetrics;