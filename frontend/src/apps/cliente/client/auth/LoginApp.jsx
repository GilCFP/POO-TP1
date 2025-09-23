import React, { useState } from 'react';
import { apiService, getCsrfToken, AuthUtils } from '../../../../shared/services/api.js';
import './login.css';

const LoginApp = () => {
  const [formData, setFormData] = useState({
    cpf: '',
    password: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

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
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const cleanCPF = AuthUtils.cleanCPF(formData.cpf);
      const response = await apiService.cliente.login(
        cleanCPF, 
        formData.password, 
        getCsrfToken()
      );

      if (response.success) {
        // Armazenar dados do cliente
        AuthUtils.setClientData(response);
        
        // Redirecionar para a página de origem ou checkout
        const urlParams = new URLSearchParams(window.location.search);
        const next = urlParams.get('next') || '/pedidos/checkout/';
        window.location.href = next;
      } else {
        setError(response.error || 'Erro no login');
      }
    } catch (error) {
      console.error('Erro no login:', error);
      setError(error.message || 'Erro de conexão. Tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  const handleTemporaryUser = async () => {
    try {
      // Redirecionar para página de criação de usuário temporário
      window.location.href = '/clientes/register/?type=temporary';
    } catch (error) {
      console.error('Erro ao redirecionar:', error);
    }
  };

  return (
    <div className="login-container">
      <h1>Login</h1>
      
      <form onSubmit={handleSubmit} className="login-form">
        <div className="form-group">
          <label htmlFor="cpf">CPF:</label>
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
          <div className="help-text">
            Insira seu CPF (com ou sem pontos e traços)
          </div>
        </div>
        
        <div className="form-group">
          <label htmlFor="password">Senha:</label>
          <input
            type="password"
            id="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            required
            placeholder="Sua senha"
          />
        </div>
        
        <button 
          type="submit" 
          className="btn btn-primary"
          disabled={loading}
        >
          {loading ? 'Entrando...' : 'Entrar'}
        </button>
      </form>
      
      <div className="links">
        <button 
          type="button"
          onClick={handleTemporaryUser}
          className="btn btn-secondary"
        >
          Continuar como usuário temporário
        </button>
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

export default LoginApp;