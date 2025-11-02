/**
 * useDashboardData - Hook para gerenciar dados do dashboard
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import DashboardService from '../services/dashboardService';

export const useDashboardData = (period = 7, restauranteId = 1) => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [lastUpdated, setLastUpdated] = useState(null);
    
    // Ref para evitar múltiplas requisições simultâneas
    const fetchingRef = useRef(false);
    
    /**
     * Função para buscar dados do dashboard
     */
    const fetchData = useCallback(async (showLoading = true) => {
        // Evitar múltiplas requisições simultâneas
        if (fetchingRef.current) {
            return;
        }
        
        try {
            fetchingRef.current = true;
            
            if (showLoading) {
                setLoading(true);
            }
            setError(null);
            
            // Verificar se a configuração é válida
            if (!DashboardService.isConfigValid()) {
                throw new Error('Configuração do dashboard não encontrada ou inválida');
            }
            
            // Buscar dados
            const result = await DashboardService.fetchAllData(period, restauranteId);
            
            // Verificar se há pelo menos alguns dados válidos
            const hasValidData = result.metrics || result.salesChart || result.topProducts;
            
            if (!hasValidData) {
                throw new Error('Nenhum dado válido foi retornado do servidor');
            }
            
            setData(result);
            setLastUpdated(new Date());
            
        } catch (err) {
            console.error('Erro ao buscar dados do dashboard:', err);
            setError(err.message || 'Erro desconhecido ao carregar dados');
            
            // Se não há dados anteriores, definir estrutura vazia
            if (!data) {
                setData({
                    metrics: null,
                    salesChart: null,
                    topProducts: null
                });
            }
        } finally {
            setLoading(false);
            fetchingRef.current = false;
        }
    }, [period, restauranteId, data]);
    
    /**
     * Função para forçar atualização dos dados
     */
    const refetch = useCallback(() => {
        fetchData(true);
    }, [fetchData]);
    
    /**
     * Função para atualização silenciosa (sem loading)
     */
    const silentRefresh = useCallback(() => {
        fetchData(false);
    }, [fetchData]);
    
    // Buscar dados quando o período ou restaurante mudar
    useEffect(() => {
        fetchData(true);
    }, [period, restauranteId]);
    
    // Auto refresh (se configurado)
    useEffect(() => {
        const autoRefreshInterval = window.DASHBOARD_CONFIG?.settings?.autoRefreshInterval;
        
        if (autoRefreshInterval && autoRefreshInterval > 0) {
            const interval = setInterval(() => {
                silentRefresh();
            }, autoRefreshInterval);
            
            return () => clearInterval(interval);
        }
    }, [silentRefresh]);
    
    // Cleanup ao desmontar
    useEffect(() => {
        return () => {
            fetchingRef.current = false;
        };
    }, []);
    
    return {
        data,
        loading,
        error,
        lastUpdated,
        refetch,
        silentRefresh,
        
        // Getters para dados específicos
        get metrics() {
            return data?.metrics || null;
        },
        
        get salesChart() {
            return data?.salesChart || null;
        },
        
        get topProducts() {
            return data?.topProducts || null;
        },
        
        get hasData() {
            return !!(data?.metrics || data?.salesChart || data?.topProducts);
        },
        
        get hasError() {
            return !!error;
        },
        
        get isLoading() {
            return loading;
        }
    };
};