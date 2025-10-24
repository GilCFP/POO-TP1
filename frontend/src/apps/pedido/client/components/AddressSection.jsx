import React from 'react';

const AddressSection = ({ address, onAddressChange, deliveryType }) => {
  // Se for retirada, não mostra o formulário de endereço
  if (deliveryType === 'pickup') {
    return (
      <div className="section-card">
        <div className="section-header">
          <h5 className="mb-0">🏪 Retirada no Local</h5>
        </div>
        <div className="section-body">
          <div className="alert alert-info">
            <strong>Endereço para retirada:</strong><br/>
            Rua das Flores, 123 - Centro<br/>
            Horário: Segunda a Sábado, 10h às 22h
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="section-card">
      <div className="section-header">
        <h5 className="mb-0">📍 Endereço de Entrega</h5>
      </div>
      <div className="section-body">
        <div className="row">
          <div className="col-md-8">
            <div className="form-group mb-3">
              <label htmlFor="street" className="form-label">Rua e Número *</label>
              <input
                type="text"
                id="street"
                name="street"
                className="form-control"
                value={address.street || ''}
                onChange={(e) => onAddressChange({ ...address, street: e.target.value })}
                placeholder="Ex: Rua das Flores, 123"
                required
              />
            </div>
          </div>
          <div className="col-md-4">
            <div className="form-group mb-3">
              <label htmlFor="neighborhood" className="form-label">Bairro *</label>
              <input
                type="text"
                id="neighborhood"
                name="neighborhood"
                className="form-control"
                value={address.neighborhood || ''}
                onChange={(e) => onAddressChange({ ...address, neighborhood: e.target.value })}
                placeholder="Ex: Centro"
                required
              />
            </div>
          </div>
        </div>

        <div className="row">
          <div className="col-md-6">
            <div className="form-group mb-3">
              <label htmlFor="complement" className="form-label">Complemento</label>
              <input
                type="text"
                id="complement"
                name="complement"
                className="form-control"
                value={address.complement || ''}
                onChange={(e) => onAddressChange({ ...address, complement: e.target.value })}
                placeholder="Apt, Bloco, etc. (opcional)"
              />
            </div>
          </div>
          <div className="col-md-6">
            <div className="form-group mb-3">
              <label htmlFor="reference" className="form-label">Ponto de Referência</label>
              <input
                type="text"
                id="reference"
                name="reference"
                className="form-control"
                value={address.reference || ''}
                onChange={(e) => onAddressChange({ ...address, reference: e.target.value })}
                placeholder="Próximo ao shopping (opcional)"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AddressSection;