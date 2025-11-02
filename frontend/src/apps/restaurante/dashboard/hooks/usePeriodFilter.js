/**
 * usePeriodFilter - Hook para gerenciar filtros de período do dashboard
 */

import { useState, useEffect, useCallback } from 'react';

export const usePeriodFilter = () => {
    const [period, setPeriodState] = useState(() => {
        // Recuperar do localStorage ou usar padrão
        const saved = localStorage.getItem('dashboard_period');
        const defaultPeriod = window.DASHBOARD_CONFIG?.settings?.defaultPeriod || 7;
        
        if (saved) {
            const parsed = parseInt(saved);
            return isNaN(parsed) ? defaultPeriod : parsed;
        }
        
        return defaultPeriod;
    });
    
    const [customDates, setCustomDates] = useState({
        startDate: '',
        endDate: ''
    });
    
    // Opções de período predefinidas
    const periodOptions = [
        { value: 7, label: 'Últimos 7 dias', shortLabel: '7d' },
        { value: 30, label: 'Últimos 30 dias', shortLabel: '30d' },
        { value: 90, label: 'Últimos 3 meses', shortLabel: '3m' },
        { value: 365, label: 'Último ano', shortLabel: '1a' },
        { value: 'custom', label: 'Período customizado', shortLabel: 'Custom' }
    ];
    
    /**
     * Função para alterar o período
     */
    const setPeriod = useCallback((newPeriod) => {
        // Validar período
        const maxPeriod = window.DASHBOARD_CONFIG?.settings?.maxPeriod || 365;
        
        if (typeof newPeriod === 'number') {
            if (newPeriod <= 0 || newPeriod > maxPeriod) {
                console.warn(`Período inválido: ${newPeriod}. Deve estar entre 1 e ${maxPeriod}`);
                return;
            }
        } else if (newPeriod !== 'custom') {
            console.warn(`Tipo de período inválido: ${newPeriod}`);
            return;
        }
        
        setPeriodState(newPeriod);
    }, []);
    
    /**
     * Função para definir datas customizadas
     */
    const setCustomDateRange = useCallback((startDate, endDate) => {
        // Validar datas
        const start = new Date(startDate);
        const end = new Date(endDate);
        const now = new Date();
        
        if (isNaN(start.getTime()) || isNaN(end.getTime())) {
            throw new Error('Datas inválidas fornecidas');
        }
        
        if (start > end) {
            throw new Error('Data inicial não pode ser posterior à data final');
        }
        
        if (start > now) {
            throw new Error('Data inicial não pode ser no futuro');
        }
        
        // Calcular diferença em dias
        const diffTime = Math.abs(end - start);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        const maxPeriod = window.DASHBOARD_CONFIG?.settings?.maxPeriod || 365;
        
        if (diffDays > maxPeriod) {
            throw new Error(`Período não pode exceder ${maxPeriod} dias`);
        }
        
        setCustomDates({ startDate, endDate });
        setPeriodState('custom');
    }, []);
    
    /**
     * Calcula as datas efetivas baseadas no período atual
     */
    const getEffectiveDates = useCallback(() => {
        if (period === 'custom') {
            return {
                startDate: customDates.startDate,
                endDate: customDates.endDate,
                days: customDates.startDate && customDates.endDate 
                    ? Math.ceil((new Date(customDates.endDate) - new Date(customDates.startDate)) / (1000 * 60 * 60 * 24))
                    : 0
            };
        }
        
        const end = new Date();
        const start = new Date();
        start.setDate(start.getDate() - period);
        
        return {
            startDate: start.toISOString().split('T')[0],
            endDate: end.toISOString().split('T')[0],
            days: period
        };
    }, [period, customDates]);
    
    /**
     * Encontra a opção de período atual
     */
    const getCurrentOption = useCallback(() => {
        return periodOptions.find(option => option.value === period) || null;
    }, [period, periodOptions]);
    
    /**
     * Verifica se o período atual é customizado
     */
    const isCustomPeriod = period === 'custom';
    
    /**
     * Verifica se as datas customizadas são válidas
     */
    const isCustomDatesValid = useCallback(() => {
        if (!isCustomPeriod) return true;
        
        return customDates.startDate && 
               customDates.endDate && 
               new Date(customDates.startDate) <= new Date(customDates.endDate);
    }, [isCustomPeriod, customDates]);
    
    // Salvar período no localStorage quando mudar
    useEffect(() => {
        if (typeof period === 'number') {
            localStorage.setItem('dashboard_period', period.toString());
        } else {
            localStorage.setItem('dashboard_period', 'custom');
        }
    }, [period]);
    
    // Salvar datas customizadas no localStorage
    useEffect(() => {
        if (isCustomPeriod) {
            localStorage.setItem('dashboard_custom_dates', JSON.stringify(customDates));
        }
    }, [isCustomPeriod, customDates]);
    
    // Recuperar datas customizadas ao inicializar
    useEffect(() => {
        const savedCustomDates = localStorage.getItem('dashboard_custom_dates');
        if (savedCustomDates) {
            try {
                const parsed = JSON.parse(savedCustomDates);
                if (parsed.startDate && parsed.endDate) {
                    setCustomDates(parsed);
                }
            } catch (error) {
                console.warn('Erro ao recuperar datas customizadas:', error);
            }
        }
    }, []);
    
    return {
        period,
        setPeriod,
        customDates,
        setCustomDateRange,
        periodOptions,
        isCustomPeriod,
        isCustomDatesValid: isCustomDatesValid(),
        getCurrentOption: getCurrentOption(),
        getEffectiveDates: getEffectiveDates(),
        
        // Helpers
        get periodLabel() {
            const option = getCurrentOption();
            return option ? option.label : 'Período customizado';
        },
        
        get periodShortLabel() {
            const option = getCurrentOption();
            return option ? option.shortLabel : 'Custom';
        }
    };
};