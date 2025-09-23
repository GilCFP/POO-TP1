import React, { useState } from 'react';

const PaymentSection = ({ payment, onPaymentChange, errors = {} }) => {
  const [selectedMethod, setSelectedMethod] = useState(payment.method || 'card');

  const handleMethodChange = (method) => {
    setSelectedMethod(method);
    onPaymentChange({ ...payment, method });
  };

  return (
    <div className="payment-section">
      <h3>Forma de Pagamento</h3>
      
      <div className="payment-methods">
        <div className="method-options">
          <label className={`method-option ${selectedMethod === 'card' ? 'selected' : ''}`}>
            <input
              type="radio"
              name="paymentMethod"
              value="card"
              checked={selectedMethod === 'card'}
              onChange={() => handleMethodChange('card')}
            />
            <div className="method-content">
              <span className="method-icon">💳</span>
              <span className="method-name">Cartão de Crédito/Débito</span>
            </div>
          </label>

          <label className={`method-option ${selectedMethod === 'pix' ? 'selected' : ''}`}>
            <input
              type="radio"
              name="paymentMethod"
              value="pix"
              checked={selectedMethod === 'pix'}
              onChange={() => handleMethodChange('pix')}
            />
            <div className="method-content">
              <span className="method-icon">📱</span>
              <span className="method-name">PIX</span>
            </div>
          </label>

          <label className={`method-option ${selectedMethod === 'money' ? 'selected' : ''}`}>
            <input
              type="radio"
              name="paymentMethod"
              value="money"
              checked={selectedMethod === 'money'}
              onChange={() => handleMethodChange('money')}
            />
            <div className="method-content">
              <span className="method-icon">💵</span>
              <span className="method-name">Dinheiro</span>
            </div>
          </label>
        </div>

        {/* Formulário específico para cartão */}
        {selectedMethod === 'card' && (
          <div className="card-form">
            <div className="form-group">
              <label htmlFor="cardNumber">Número do Cartão</label>
              <input
                type="text"
                id="cardNumber"
                name="cardNumber"
                value={payment.cardNumber || ''}
                onChange={(e) => onPaymentChange({ ...payment, cardNumber: e.target.value })}
                className={errors.cardNumber ? 'error' : ''}
                placeholder="1234 5678 9012 3456"
                maxLength={19}
              />
              {errors.cardNumber && <span className="error-message">{errors.cardNumber}</span>}
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="cardExpiry">Validade</label>
                <input
                  type="text"
                  id="cardExpiry"
                  name="cardExpiry"
                  value={payment.cardExpiry || ''}
                  onChange={(e) => onPaymentChange({ ...payment, cardExpiry: e.target.value })}
                  className={errors.cardExpiry ? 'error' : ''}
                  placeholder="MM/AA"
                  maxLength={5}
                />
                {errors.cardExpiry && <span className="error-message">{errors.cardExpiry}</span>}
              </div>

              <div className="form-group">
                <label htmlFor="cardCvv">CVV</label>
                <input
                  type="text"
                  id="cardCvv"
                  name="cardCvv"
                  value={payment.cardCvv || ''}
                  onChange={(e) => onPaymentChange({ ...payment, cardCvv: e.target.value })}
                  className={errors.cardCvv ? 'error' : ''}
                  placeholder="123"
                  maxLength={4}
                />
                {errors.cardCvv && <span className="error-message">{errors.cardCvv}</span>}
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="cardName">Nome no Cartão</label>
              <input
                type="text"
                id="cardName"
                name="cardName"
                value={payment.cardName || ''}
                onChange={(e) => onPaymentChange({ ...payment, cardName: e.target.value })}
                className={errors.cardName ? 'error' : ''}
                placeholder="Nome como está no cartão"
              />
              {errors.cardName && <span className="error-message">{errors.cardName}</span>}
            </div>
          </div>
        )}

        {/* Informação para PIX */}
        {selectedMethod === 'pix' && (
          <div className="pix-info">
            <div className="info-box">
              <p>🔒 Pagamento 100% seguro via PIX</p>
              <p>Você receberá o código PIX após a confirmação do pedido</p>
            </div>
          </div>
        )}

        {/* Informação para dinheiro */}
        {selectedMethod === 'money' && (
          <div className="money-form">
            <div className="form-group">
              <label htmlFor="changeFor">Troco para:</label>
              <input
                type="number"
                id="changeFor"
                name="changeFor"
                value={payment.changeFor || ''}
                onChange={(e) => onPaymentChange({ ...payment, changeFor: e.target.value })}
                placeholder="Ex: 50.00 (deixe vazio se não precisar de troco)"
                min="0"
                step="0.01"
              />
            </div>
            <div className="info-box">
              <p>💵 Tenha o valor exato ou informe o valor para troco</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PaymentSection;