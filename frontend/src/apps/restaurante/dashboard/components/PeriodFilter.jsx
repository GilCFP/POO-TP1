/**
 * PeriodFilter - Componente para filtrar período do dashboard
 */

import React, { useState } from 'react';

const PeriodFilter = ({ 
    selectedPeriod, 
    onPeriodChange, 
    periodOptions, 
    isCustomPeriod,
    onCustomDateChange,
    isCustomDatesValid 
}) => {
    const [showCustomPicker, setShowCustomPicker] = useState(isCustomPeriod);
    const [customStartDate, setCustomStartDate] = useState('');
    const [customEndDate, setCustomEndDate] = useState('');
    const [dateError, setDateError] = useState('');
    
    /**
     * Handler para mudança de período predefinido
     */
    const handlePeriodClick = (period) => {
        if (period === 'custom') {
            setShowCustomPicker(true);
        } else {
            setShowCustomPicker(false);
            setDateError('');
        }
        onPeriodChange(period);
    };
    
    /**
     * Handler para aplicar datas customizadas
     */
    const handleApplyCustomDates = () => {
        if (!customStartDate || !customEndDate) {
            setDateError('Ambas as datas são obrigatórias');
            return;
        }
        
        const startDate = new Date(customStartDate);
        const endDate = new Date(customEndDate);
        const today = new Date();
        today.setHours(23, 59, 59, 999); // Fim do dia de hoje
        
        // Validações
        if (startDate > endDate) {
            setDateError('Data inicial não pode ser posterior à data final');
            return;
        }
        
        if (startDate > today) {
            setDateError('Data inicial não pode ser no futuro');
            return;
        }
        
        if (endDate > today) {
            setDateError('Data final não pode ser no futuro');
            return;
        }
        
        // Verificar limite de dias
        const diffTime = Math.abs(endDate - startDate);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        const maxDays = 365; // Pode vir de configuração
        
        if (diffDays > maxDays) {
            setDateError(`Período não pode exceder ${maxDays} dias`);
            return;
        }
        
        try {
            setDateError('');
            onCustomDateChange(customStartDate, customEndDate);
        } catch (error) {
            setDateError(error.message);
        }
    };
    
    /**
     * Handler para cancelar seleção customizada
     */
    const handleCancelCustom = () => {
        setShowCustomPicker(false);
        setDateError('');
        
        // Voltar para o primeiro período predefinido
        const firstPredefined = periodOptions.find(opt => opt.value !== 'custom');
        if (firstPredefined) {
            onPeriodChange(firstPredefined.value);
        }
    };
    
    /**
     * Gera data padrão para inputs (hoje e 7 dias atrás)
     */
    const getDefaultDates = () => {
        const today = new Date();
        const weekAgo = new Date();
        weekAgo.setDate(weekAgo.getDate() - 7);
        
        return {
            end: today.toISOString().split('T')[0],
            start: weekAgo.toISOString().split('T')[0]
        };
    };
    
    // Inicializar datas se estiverem vazias
    React.useEffect(() => {
        if (showCustomPicker && !customStartDate && !customEndDate) {
            const defaults = getDefaultDates();
            setCustomStartDate(defaults.start);
            setCustomEndDate(defaults.end);
        }
    }, [showCustomPicker, customStartDate, customEndDate]);
    
    return (
        <div className="period-filters">
            <div className="filter-label">
                <span>📅 Período:</span>
            </div>
            
            {/* Botões de período predefinido */}
            <div className="period-buttons">
                {periodOptions.map((option) => (
                    <button
                        key={option.value}
                        className={`period-filter-btn ${selectedPeriod === option.value ? 'active' : ''}`}
                        onClick={() => handlePeriodClick(option.value)}
                        title={option.label}
                    >
                        {option.shortLabel || option.label}
                    </button>
                ))}
            </div>
            
            {/* Seletor de datas customizadas */}
            {showCustomPicker && (
                <div className="custom-date-picker">
                    <div className="date-inputs">
                        <div className="date-input-group">
                            <label htmlFor="start-date">Data inicial:</label>
                            <input
                                id="start-date"
                                type="date"
                                value={customStartDate}
                                onChange={(e) => setCustomStartDate(e.target.value)}
                                max={new Date().toISOString().split('T')[0]}
                            />
                        </div>
                        
                        <div className="date-input-group">
                            <label htmlFor="end-date">Data final:</label>
                            <input
                                id="end-date"
                                type="date"
                                value={customEndDate}
                                onChange={(e) => setCustomEndDate(e.target.value)}
                                max={new Date().toISOString().split('T')[0]}
                                min={customStartDate}
                            />
                        </div>
                    </div>
                    
                    <div className="date-actions">
                        <button
                            className="btn btn-primary btn-sm"
                            onClick={handleApplyCustomDates}
                            disabled={!customStartDate || !customEndDate}
                        >
                            Aplicar
                        </button>
                        <button
                            className="btn btn-secondary btn-sm"
                            onClick={handleCancelCustom}
                        >
                            Cancelar
                        </button>
                    </div>
                    
                    {dateError && (
                        <div className="date-error">
                            <small>{dateError}</small>
                        </div>
                    )}
                </div>
            )}
            
            {/* Indicador de período ativo */}
            <div className="active-period-indicator">
                {isCustomPeriod && isCustomDatesValid ? (
                    <small>
                        <strong>Período customizado:</strong> {customStartDate} até {customEndDate}
                    </small>
                ) : !isCustomPeriod && (
                    <small>
                        <strong>Período:</strong> {periodOptions.find(opt => opt.value === selectedPeriod)?.label}
                    </small>
                )}
            </div>
        </div>
    );
};

export default PeriodFilter;