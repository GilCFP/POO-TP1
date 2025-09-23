import React from 'react';

const AddressSection = ({ address, onAddressChange, errors = {} }) => {
  return (
    <div className="address-section">
      <h3>Endereço de Entrega</h3>
      
      <div className="address-form">
        <div className="form-group">
          <label htmlFor="street">Rua/Avenida</label>
          <input
            type="text"
            id="street"
            name="street"
            value={address.street || ''}
            onChange={(e) => onAddressChange({ ...address, street: e.target.value })}
            className={errors.street ? 'error' : ''}
            placeholder="Nome da rua, número"
          />
          {errors.street && <span className="error-message">{errors.street}</span>}
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="neighborhood">Bairro</label>
            <input
              type="text"
              id="neighborhood"
              name="neighborhood"
              value={address.neighborhood || ''}
              onChange={(e) => onAddressChange({ ...address, neighborhood: e.target.value })}
              className={errors.neighborhood ? 'error' : ''}
              placeholder="Bairro"
            />
            {errors.neighborhood && <span className="error-message">{errors.neighborhood}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="city">Cidade</label>
            <input
              type="text"
              id="city"
              name="city"
              value={address.city || ''}
              onChange={(e) => onAddressChange({ ...address, city: e.target.value })}
              className={errors.city ? 'error' : ''}
              placeholder="Cidade"
            />
            {errors.city && <span className="error-message">{errors.city}</span>}
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="zipCode">CEP</label>
            <input
              type="text"
              id="zipCode"
              name="zipCode"
              value={address.zipCode || ''}
              onChange={(e) => onAddressChange({ ...address, zipCode: e.target.value })}
              className={errors.zipCode ? 'error' : ''}
              placeholder="00000-000"
              maxLength={9}
            />
            {errors.zipCode && <span className="error-message">{errors.zipCode}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="complement">Complemento</label>
            <input
              type="text"
              id="complement"
              name="complement"
              value={address.complement || ''}
              onChange={(e) => onAddressChange({ ...address, complement: e.target.value })}
              placeholder="Apartamento, bloco, etc. (opcional)"
            />
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="reference">Ponto de Referência</label>
          <input
            type="text"
            id="reference"
            name="reference"
            value={address.reference || ''}
            onChange={(e) => onAddressChange({ ...address, reference: e.target.value })}
            placeholder="Próximo ao shopping, em frente à escola... (opcional)"
          />
        </div>
      </div>
    </div>
  );
};

export default AddressSection;