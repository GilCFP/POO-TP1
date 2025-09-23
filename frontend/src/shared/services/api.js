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
      this.get(`/produto/cardapio/?${new URLSearchParams(params)}`),
    
    getDetalhes: (produtoId) => 
      this.get(`/produto/${produtoId}/`),
    
    addToCart: (produtoId, quantidade, csrfToken) => 
      this.post('/produto/add-to-cart/', { produto_id: produtoId, quantidade }, csrfToken),
  };

  cliente = {
    getProfile: () => 
      this.get('/cliente/profile/'),
    
    updateProfile: (data, csrfToken) => 
      this.put('/cliente/profile/', data, csrfToken),
    
    getEnderecos: () => 
      this.get('/cliente/enderecos/'),
    
    addEndereco: (endereco, csrfToken) => 
      this.post('/cliente/enderecos/', endereco, csrfToken),
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