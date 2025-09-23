import React from 'react';
import clsx from 'clsx';

/**
 * Componente para seleção do tipo de entrega
 */
const DeliveryOptions = ({ selected, onChange }) => {
  const options = [
    {
      id: 'delivery',
      icon: '🚚',
      title: 'Entrega',
      subtitle: 'Taxa: R$ 5,00 • 30-45 min',
      fee: 5.00
    },
    {
      id: 'pickup',
      icon: '🏪',
      title: 'Retirada',
      subtitle: 'Grátis • 15-20 min',
      fee: 0
    }
  ];

  return (
    <div className="section-card">
      <div className="section-header">
        <h5 className="mb-0">🚛 Tipo de Entrega</h5>
      </div>
      <div className="section-body">
        <div className="option-grid">
          {options.map((option) => (
            <label
              key={option.id}
              className={clsx('option-card', {
                selected: selected === option.id
              })}
              onClick={() => onChange(option.id)}
            >
              <input
                type="radio"
                name="delivery_type"
                value={option.id}
                checked={selected === option.id}
                onChange={() => onChange(option.id)}
              />
              <span className="option-icon">{option.icon}</span>
              <div className="option-title">{option.title}</div>
              <div className="option-subtitle">{option.subtitle}</div>
            </label>
          ))}
        </div>
      </div>
    </div>
  );
};

export default DeliveryOptions;