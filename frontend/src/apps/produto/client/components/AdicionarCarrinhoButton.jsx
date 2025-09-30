import React, { useState } from 'react';
import { useCarrinho } from '@pedido/shared/hooks/useCarrinho';
import LoadingSpinner from '@components/common/LoadingSpinner';
import './AdicionarCarrinhoButton.css';

/**
 * Componente de botão para adicionar produto ao carrinho
 */
const AdicionarCarrinhoButton = ({ 
  produto, 
  quantidade = 1, 
  className = '', 
  disabled = false,
  onSuccess,
  onError
}) => {
  const [localLoading, setLocalLoading] = useState(false);
  const [feedback, setFeedback] = useState('');
  const [feedbackType, setFeedbackType] = useState(''); // 'success' | 'error'
  
  const { adicionarProduto, loading: carrinhoLoading } = useCarrinho();

  const isLoading = localLoading || carrinhoLoading;

  const handleAdicionarCarrinho = async () => {
    if (isLoading || disabled) return;

    try {
      setLocalLoading(true);
      setFeedback('');

      const resultado = await adicionarProduto(produto.id, quantidade);

      if (resultado.success) {
        setFeedback(resultado.message);
        setFeedbackType('success');
        
        // Callback de sucesso
        if (onSuccess) {
          onSuccess(resultado);
        }

        // Limpa feedback após 3 segundos
        setTimeout(() => {
          setFeedback('');
          setFeedbackType('');
        }, 3000);
      } else {
        setFeedback(resultado.error);
        setFeedbackType('error');
        
        // Callback de erro
        if (onError) {
          onError(resultado);
        }
      }
    } catch (error) {
      setFeedback('Erro inesperado ao adicionar produto');
      setFeedbackType('error');
      
      if (onError) {
        onError({ success: false, error: error.message });
      }
    } finally {
      setLocalLoading(false);
    }
  };

  const getButtonClass = () => {
    let buttonClass = `adicionar-carrinho-btn ${className}`;
    
    if (isLoading) buttonClass += ' loading';
    if (disabled) buttonClass += ' disabled';
    if (feedbackType) buttonClass += ` ${feedbackType}`;
    
    return buttonClass;
  };

  const getButtonText = () => {
    if (isLoading) return 'Adicionando...';
    if (feedbackType === 'success') return '✓ Adicionado!';
    if (feedbackType === 'error') return 'Erro - Tentar novamente';
    return 'Adicionar ao Carrinho';
  };

  return (
    <div className="adicionar-carrinho-container">
      <button
        className={getButtonClass()}
        onClick={handleAdicionarCarrinho}
        disabled={isLoading || disabled}
        type="button"
      >
        {isLoading && <LoadingSpinner size="small" />}
        <span className="button-text">{getButtonText()}</span>
      </button>
      
      {feedback && (
        <div className={`feedback-message ${feedbackType}`}>
          {feedback}
        </div>
      )}
    </div>
  );
};

export default AdicionarCarrinhoButton;