import React, { useState, useEffect } from 'react';
import { apiService, getCsrfToken, AuthUtils } from '../../../../shared/services/api.js';
import './register.css';

const RegisterApp = () => {
  const [formData, setFormData] = useState({
    cpf: '',
    name: '',
    phone: '',
    email: '',
    password: '',
    confirmPassword: '',
    address: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [registrationType, setRegistrationType] = useState('temporary');

  useEffect(() => {
    // Verificar tipo de registro pela URL
    const urlParams = new URLSearchParams(window.location.search);
    const type = urlParams.get('type');
    if (type === 'permanent') {
      setRegistrationType('permanent');
    }
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    
    if (name === 'cpf') {
      // Aplicar máscara de CPF
      const cleanValue = value.replace(/\D/g, '');
      const maskedValue = cleanValue
        .replace(/(\d{3})(\d)/, '$1.$2')
        .replace(/(\d{3})(\d)/, '$1.$2')
        .replace(/(\d{3})(\d{1,2})$/, '$1-$2');
      
      setFormData(prev => ({
        ...prev,
        [name]: maskedValue
      }));
    } else if (name === 'phone') {
      // Aplicar máscara de telefone
      const cleanValue = value.replace(/\D/g, '');
      let maskedValue = cleanValue;
      
      if (cleanValue.length <= 10) {
        maskedValue = cleanValue.replace(/(\d{2})(\d{4})(\d{4})/, '($1) $2-$3');
      } else {
        maskedValue = cleanValue.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
      }
      
      setFormData(prev => ({
        ...prev,
        [name]: maskedValue
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }));
    }
  };

  const validateForm = () => {
    if (!formData.cpf || !formData.name || !formData.phone) {
      setError('CPF, nome e telefone são obrigatórios');
      return false;
    }

    if (registrationType === 'permanent') {
      if (!formData.email || !formData.password) {
        setError('Email e senha são obrigatórios para conta permanente');
        return false;
      }

      if (formData.password !== formData.confirmPassword) {
        setError('As senhas não coincidem');
        return false;
      }

      if (formData.password.length < 6) {
        setError('A senha deve ter pelo menos 6 caracteres');
        return false;
      }
    }

    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!validateForm()) {
      return;
    }

    setLoading(true);

    try {
      const cleanCPF = AuthUtils.cleanCPF(formData.cpf);
      const cleanPhone = formData.phone.replace(/\D/g, '');
      
      let response;

      if (registrationType === 'temporary') {
        response = await apiService.cliente.createTemporary(
          cleanCPF, 
          formData.name, 
          cleanPhone, 
          getCsrfToken()
        );
      } else {
        response = await apiService.cliente.createPermanent({
          cpf: cleanCPF,
          name: formData.name,
          phone: cleanPhone,
          email: formData.email,
          password: formData.password,
          address: formData.address
        }, getCsrfToken());
      }

      if (response.success) {
        // Armazenar dados do cliente
        AuthUtils.setClientData(response);
        
        // Redirecionar para a página de origem ou checkout
        const urlParams = new URLSearchParams(window.location.search);
        const next = urlParams.get('next') || '/pedidos/checkout/';
        window.location.href = next;
      } else {
        setError(response.error || 'Erro no cadastro');
      }
    } catch (error) {
      console.error('Erro no cadastro:', error);
      setError(error.message || 'Erro de conexão. Tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  const switchRegistrationType = (type) => {
    setRegistrationType(type);
    setError('');
  };

  return (
    <div className="register-container">
      <h1>
        {registrationType === 'temporary' ? 'Usuário Temporário' : 'Conta Permanente'}
      </h1>
      
      <div className="register-type-selector">
        <button 
          type="button"
          className={`btn ${registrationType === 'temporary' ? 'btn-primary' : 'btn-outline'}`}
          onClick={() => switchRegistrationType('temporary')}
        >
          Temporário
        </button>
        <button 
          type="button"
          className={`btn ${registrationType === 'permanent' ? 'btn-primary' : 'btn-outline'}`}
          onClick={() => switchRegistrationType('permanent')}
        >
          Permanente
        </button>
      </div>

      <p className="register-description">
        {registrationType === 'temporary' 
          ? 'Acesso rápido apenas com CPF, nome e telefone. Dados podem ser limpos automaticamente.'
          : 'Conta completa com email e senha para acesso futuro.'
        }
      </p>
      
      <form onSubmit={handleSubmit} className="register-form">
        <div className="form-group">
          <label htmlFor="cpf">CPF: *</label>
          <input
            type="text"
            id="cpf"
            name="cpf"
            value={formData.cpf}
            onChange={handleChange}
            required
            placeholder="000.000.000-00"
            maxLength="14"
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="name">Nome: *</label>
          <input
            type="text"
            id="name"
            name="name"
            value={formData.name}
            onChange={handleChange}
            required
            placeholder="Seu nome completo"
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="phone">Telefone: *</label>
          <input
            type="text"
            id="phone"
            name="phone"
            value={formData.phone}
            onChange={handleChange}
            required
            placeholder="(11) 99999-9999"
            maxLength="15"
          />
        </div>

        {registrationType === 'permanent' && (
          <>
            <div className="form-group">
              <label htmlFor="email">Email: *</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
                placeholder="seu@email.com"
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="password">Senha: *</label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                required
                placeholder="Mínimo 6 caracteres"
                minLength="6"
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="confirmPassword">Confirmar Senha: *</label>
              <input
                type="password"
                id="confirmPassword"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                required
                placeholder="Confirme sua senha"
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="address">Endereço:</label>
              <textarea
                id="address"
                name="address"
                value={formData.address}
                onChange={handleChange}
                placeholder="Seu endereço completo (opcional)"
                rows="3"
              />
            </div>
          </>
        )}
        
        <button 
          type="submit" 
          className="btn btn-primary"
          disabled={loading}
        >
          {loading ? 'Criando...' : (registrationType === 'temporary' ? 'Criar Usuário Temporário' : 'Criar Conta Permanente')}
        </button>
      </form>
      
      <div className="links">
        <p>
          <a href="/clientes/login/">Já tem conta? Faça login</a>
        </p>
        <p>
          <a href="/">Voltar ao início</a>
        </p>
      </div>
      
      {error && (
        <div className="error">
          {error}
        </div>
      )}
    </div>
  );
};

export default RegisterApp;