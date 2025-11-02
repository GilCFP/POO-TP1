/**
 * Serviço de API para comunicação com o backend Django
 */
class ApiService {
  constructor() {
    this.baseURL = '';
    this.defaultHeaders = {
      'Content-Type': 'application/json',
    };
  }

  /**
   * Método GET
   */
  async get(url, headers = {}) {
    try {
      const response = await fetch(this.baseURL + url, {
        method: 'GET',
        headers: { ...this.defaultHeaders, ...headers },
      });

      return await this.handleResponse(response);
    } catch (error) {
      console.error('Erro na requisição GET:', error);
      throw error;
    }
  }

  /**
   * Método POST
   */
  async post(url, data = null, csrfToken = null, headers = {}) {
    try {
      const requestHeaders = { ...this.defaultHeaders, ...headers };
      
      if (csrfToken) {
        requestHeaders['X-CSRFToken'] = csrfToken;
      }

      const response = await fetch(this.baseURL + url, {
        method: 'POST',
        headers: requestHeaders,
        body: data ? JSON.stringify(data) : null,
      });

      return await this.handleResponse(response);
    } catch (error) {
      console.error('Erro na requisição POST:', error);
      throw error;
    }
  }

  /**
   * Método PUT
   */
  async put(url, data = null, csrfToken = null, headers = {}) {
    try {
      const requestHeaders = { ...this.defaultHeaders, ...headers };
      
      if (csrfToken) {
        requestHeaders['X-CSRFToken'] = csrfToken;
      }

      const response = await fetch(this.baseURL + url, {
        method: 'PUT',
        headers: requestHeaders,
        body: data ? JSON.stringify(data) : null,
      });

      return await this.handleResponse(response);
    } catch (error) {
      console.error('Erro na requisição PUT:', error);
      throw error;
    }
  }

  /**
   * Método DELETE
   */
  async delete(url, csrfToken = null, headers = {}) {
    try {
      const requestHeaders = { ...this.defaultHeaders, ...headers };
      
      if (csrfToken) {
        requestHeaders['X-CSRFToken'] = csrfToken;
      }

      const response = await fetch(this.baseURL + url, {
        method: 'DELETE',
        headers: requestHeaders,
      });

      return await this.handleResponse(response);
    } catch (error) {
      console.error('Erro na requisição DELETE:', error);
      throw error;
    }
  }

  /**
   * Upload de arquivo
   */
  async upload(url, formData, csrfToken = null, headers = {}) {
    try {
      const requestHeaders = { ...headers }; // Não incluir Content-Type para FormData
      
      if (csrfToken) {
        requestHeaders['X-CSRFToken'] = csrfToken;
      }

      const response = await fetch(this.baseURL + url, {
        method: 'POST',
        headers: requestHeaders,
        body: formData,
      });

      return await this.handleResponse(response);
    } catch (error) {
      console.error('Erro no upload:', error);
      throw error;
    }
  }

  /**
   * Manipula a resposta da API
   */
  async handleResponse(response) {
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `HTTP Error: ${response.status}`);
    }

    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      return await response.json();
    }

    return await response.text();
  }

  /**
   * Configurações específicas para diferentes apps
   */
  pedido = {
    updateItem: (itemId, quantity, csrfToken) => 
      this.post('/pedido/update-item/', { item_id: itemId, quantity }, csrfToken),
    
    removeItem: (itemId, csrfToken) => 
      this.post('/pedido/remove-item/', { item_id: itemId }, csrfToken),
    
    getStatus: (pedidoId) => 
      this.get(`/pedido/${pedidoId}/status/`),
    
    getHistorico: (params = {}) => 
      this.get(`/pedido/historico/?${new URLSearchParams(params)}`),
  };

  produto = {
    getCardapio: (params = {}) => 
      this.get(`/produto/?${new URLSearchParams(params)}`),
    
    getDetalhes: (produtoId) => 
      this.get(`/produto/${produtoId}/`),
    
    addToCart: (produtoId, quantidade, csrfToken) => 
      this.post('/produto/add-to-cart/', { produto_id: produtoId, quantidade }, csrfToken),
  };

  cliente = {
    // Autenticação
    login: (cpf, password, csrfToken) => 
      this.post('/clientes/api/login/', { cpf, password }, csrfToken),
    
    logout: (csrfToken) => 
      this.post('/clientes/api/logout/', {}, csrfToken),
    
    createTemporary: (cpf, name, phone, csrfToken) => 
      this.post('/clientes/api/create-temporary/', { cpf, name, phone }, csrfToken),
    
    createPermanent: (data, csrfToken) => 
      this.post('/clientes/api/create-permanent/', data, csrfToken),
    
    convertToPermanent: (email, password, csrfToken) => 
      this.post('/clientes/api/convert-permanent/', { email, password }, csrfToken),
    
    // Perfil
    getCurrentClient: () => 
      this.get('/clientes/api/current/'),
    
    updateProfile: (data, csrfToken) => 
      this.put('/clientes/api/profile/update/', data, csrfToken),
    
    getProfile: () => 
      this.get('/clientes/api/profile/'),
    
    getEnderecos: () => 
      this.get('/clientes/api/enderecos/'),
    
    addEndereco: (endereco, csrfToken) => 
      this.post('/clientes/api/enderecos/', endereco, csrfToken),
  };
}

// Instância singleton
export const apiService = new ApiService();

// Export das funções utilitárias
export const getCsrfToken = () => {
  const token = document.querySelector('[name=csrfmiddlewaretoken]');
  return token ? token.value : null;
};

export const formatCurrency = (value) => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(value);
};

export const formatDate = (dateString) => {
  return new Intl.DateTimeFormat('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(new Date(dateString));
};

// Utilitários de autenticação
export const AuthUtils = {
  // Armazena dados do cliente logado
  setClientData: (clientData) => {
    localStorage.setItem('client_data', JSON.stringify(clientData));
  },
  
  // Recupera dados do cliente logado
  getClientData: () => {
    const data = localStorage.getItem('client_data');
    return data ? JSON.parse(data) : null;
  },
  
  // Remove dados do cliente (logout)
  clearClientData: () => {
    localStorage.removeItem('client_data');
  },
  
  // Verifica se cliente está logado
  isAuthenticated: () => {
    const clientData = AuthUtils.getClientData();
    const isAuth = clientData && clientData.success;
    console.log('AuthUtils.isAuthenticated - Check:', { clientData, isAuth });
    return isAuth;
  },
  
  // Obtém informações do cliente atual
  getCurrentClient: () => {
    const clientData = AuthUtils.getClientData();
    return clientData && clientData.data ? clientData.data.client : null;
  },
  
  // Verifica se é conta temporária
  isTemporaryAccount: () => {
    const clientData = AuthUtils.getClientData();
    return clientData && clientData.data && clientData.data.session 
      ? clientData.data.session.type === 'temporary' 
      : false;
  },
  
  // Formata CPF para exibição
  formatCPF: (cpf) => {
    if (!cpf) return '';
    const cleanCPF = cpf.replace(/\D/g, '');
    return cleanCPF.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
  },
  
  // Remove formatação do CPF
  cleanCPF: (cpf) => {
    return cpf ? cpf.replace(/\D/g, '') : '';
  }
};