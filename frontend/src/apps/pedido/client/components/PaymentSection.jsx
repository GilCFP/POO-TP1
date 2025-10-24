import React, { useState } from 'react';

const PaymentSection = ({ payment, onPaymentChange }) => {
  const [selectedMethod, setSelectedMethod] = useState(payment.method || 'card');

  const handleMethodChange = (method) => {
    setSelectedMethod(method);
    onPaymentChange({ ...payment, method });
  };

  return (
    <div className="section-card">
      <div className="section-header">
        <h5 className="mb-0">💳 Forma de Pagamento</h5>
      </div>
      <div className="section-body">
        <div className="payment-methods">
          <div className="option-grid">
            <label className={`option-card ${selectedMethod === 'card' ? 'selected' : ''}`}>
              <input
                type="radio"
                name="paymentMethod"
                value="card"
                checked={selectedMethod === 'card'}
                onChange={() => handleMethodChange('card')}
              />
              <span className="option-icon">💳</span>
              <div className="option-title">Cartão</div>
              <div className="option-subtitle">Crédito/Débito</div>
            </label>

            <label className={`option-card ${selectedMethod === 'pix' ? 'selected' : ''}`}>
              <input
                type="radio"
                name="paymentMethod"
                value="pix"
                checked={selectedMethod === 'pix'}
                onChange={() => handleMethodChange('pix')}
              />
              <span className="option-icon">📱</span>
              <div className="option-title">PIX</div>
              <div className="option-subtitle">Instantâneo</div>
            </label>

            <label className={`option-card ${selectedMethod === 'money' ? 'selected' : ''}`}>
              <input
                type="radio"
                name="paymentMethod"
                value="money"
                checked={selectedMethod === 'money'}
                onChange={() => handleMethodChange('money')}
              />
              <span className="option-icon">💵</span>
              <div className="option-title">Dinheiro</div>
              <div className="option-subtitle">Na entrega/retirada</div>
            </label>
          </div>

          {/* Apenas campo de troco para dinheiro */}
          {selectedMethod === 'money' && (
            <div className="mt-3">
              <div className="form-group">
                <label htmlFor="changeFor">Troco para (opcional):</label>
                <input
                  type="number"
                  id="changeFor"
                  name="changeFor"
                  className="form-control"
                  value={payment.changeFor || ''}
                  onChange={(e) => onPaymentChange({ ...payment, changeFor: e.target.value })}
                  placeholder="Ex: 50.00"
                  min="0"
                  step="0.01"
                />
                <small className="text-muted">Deixe vazio se tiver o valor exato</small>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PaymentSection;