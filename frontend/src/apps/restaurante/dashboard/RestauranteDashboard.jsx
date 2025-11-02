/**
 * RestauranteDashboard - Componente principal do dashboard de vendas
 */

import React, { useState, useEffect } from 'react';
import DashboardMetrics from './components/DashboardMetrics';
import PeriodFilter from './components/PeriodFilter';
import SalesChart from './components/SalesChart';
import TopProducts from './components/TopProducts';
import { useDashboardData } from './hooks/useDashboardData';
import { usePeriodFilter } from './hooks/usePeriodFilter';

const RestauranteDashboard = () => {
    const [restauranteId] = useState(1); // Por enquanto fixo, pode ser parametrizado
    
    // Hooks
    const { 
        period, 
        setPeriod, 
        periodOptions, 
        isCustomPeriod,
        setCustomDateRange,
        isCustomDatesValid,
        getEffectiveDates 
    } = usePeriodFilter();
    
    const { 
        data, 
        loading, 
        error, 
        lastUpdated,
        refetch,
        hasData 
    } = useDashboardData(isCustomPeriod ? getEffectiveDates.days : period, restauranteId);
    
    // Estado para controle de refresh
    const [isRefreshing, setIsRefreshing] = useState(false);
    
    /**
     * Handler para refresh manual
     */
    const handleRefresh = async () => {
        setIsRefreshing(true);
        try {
            await refetch();
        } finally {
            setIsRefreshing(false);
        }
    };
    
    /**
     * Handler para mudança de período
     */
    const handlePeriodChange = (newPeriod) => {
        setPeriod(newPeriod);
    };
    
    /**
     * Handler para datas customizadas
     */
    const handleCustomDateChange = (startDate, endDate) => {
        try {
            setCustomDateRange(startDate, endDate);
        } catch (error) {
            console.error('Erro ao definir datas customizadas:', error);
            // Aqui você pode adicionar uma notificação de erro
        }
    };
    
    // Renderização do estado de loading inicial
    if (loading && !hasData) {
        return (
            <div className="dashboard-loading">
                <div className="loading-spinner">
                    <div className="spinner"></div>
                    <p>Carregando dados do dashboard...</p>
                </div>
            </div>
        );
    }
    
    // Renderização do estado de erro (sem dados)
    if (error && !hasData) {
        return (
            <div className="dashboard-error">
                <h3>Erro ao Carregar Dashboard</h3>
                <p>{error}</p>
                <button 
                    onClick={handleRefresh} 
                    className="btn btn-primary"
                    disabled={isRefreshing}
                >
                    {isRefreshing ? 'Tentando...' : 'Tentar Novamente'}
                </button>
            </div>
        );
    }
    
    // Dados efetivos para exibição
    const effectiveDates = getEffectiveDates;
    
    return (
        <div className="dashboard-content">
            {/* Cabeçalho com filtros */}
            <div className="dashboard-controls">
                <PeriodFilter 
                    selectedPeriod={period}
                    onPeriodChange={handlePeriodChange}
                    periodOptions={periodOptions}
                    isCustomPeriod={isCustomPeriod}
                    onCustomDateChange={handleCustomDateChange}
                    isCustomDatesValid={isCustomDatesValid}
                />
                
                <div className="dashboard-status">
                    {lastUpdated && (
                        <span className="last-updated">
                            Última atualização: {lastUpdated.toLocaleTimeString('pt-BR')}
                        </span>
                    )}
                    
                    <button 
                        onClick={handleRefresh}
                        className="btn btn-refresh"
                        disabled={isRefreshing || loading}
                        title="Atualizar dados"
                    >
                        {isRefreshing ? '🔄' : '↻'}
                    </button>
                </div>
            </div>
            
            {/* Alerta de erro (com dados existentes) */}
            {error && hasData && (
                <div className="alert alert-warning">
                    <strong>Atenção:</strong> {error}
                    <button onClick={handleRefresh} className="btn btn-sm btn-warning">
                        Tentar Atualizar
                    </button>
                </div>
            )}
            
            {/* Métricas principais */}
            <DashboardMetrics 
                metrics={data?.metrics}
                loading={loading}
                period={effectiveDates}
            />
            
            {/* Gráficos e dados */}
            <div className="dashboard-charts">
                <div className="chart-section">
                    <SalesChart 
                        data={data?.salesChart}
                        loading={loading}
                        period={effectiveDates}
                    />
                </div>
                
                <div className="products-section">
                    <TopProducts 
                        products={data?.topProducts}
                        loading={loading}
                        period={effectiveDates}
                    />
                </div>
            </div>
            
            {/* Footer com informações adicionais */}
            <div className="dashboard-footer">
                <small>
                    Período: {effectiveDates.startDate} até {effectiveDates.endDate}
                    {effectiveDates.days && ` (${effectiveDates.days} dias)`}
                </small>
            </div>
        </div>
    );
};

export default RestauranteDashboard;