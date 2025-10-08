import { apiService } from '@shared/services/api';

/**
 * Serviço para gerenciar pedidos
 */
class PedidoService {
  constructor() {
    this.baseUrl = '/api/pedidos';
  }

  /**
   * Cria um novo pedido
   */
  async criarPedido(dadosPedido, csrfToken) {
    try {
      const response = await apiService.post(
        `${this.baseUrl}/criar/`,
        dadosPedido,
        csrfToken
      );
      return response;
    } catch (error) {
      console.error('Erro ao criar pedido:', error);
      throw error;
    }
  }

  /**
   * Adiciona item ao pedido
   */
  async adicionarItem(pedidoId, produtoId, quantidade = 1, instrucoesEspeciais = '', csrfToken) {
    try {
      const response = await apiService.post(
        `${this.baseUrl}/item/adicionar/`,
        {
          pedido_id: pedidoId,
          produto_id: produtoId,
          quantidade: quantidade,
          instrucoes_especiais: instrucoesEspeciais
        },
        csrfToken
      );
      return response;
    } catch (error) {
      console.error('Erro ao adicionar item:', error);
      throw error;
    }
  }

  /**
   * Remove item do pedido
   */
  async removerItem(pedidoId, produtoId, csrfToken) {
    try {
      const response = await apiService.post(
        `${this.baseUrl}/item/remover/`,
        {
          pedido_id: pedidoId,
          produto_id: produtoId
        },
        csrfToken
      );
      return response;
    } catch (error) {
      console.error('Erro ao remover item:', error);
      throw error;
    }
  }

  /**
   * Atualiza quantidade de item
   */
  async atualizarQuantidadeItem(pedidoId, produtoId, quantidade, csrfToken) {
    try {
      const response = await apiService.post(
        `${this.baseUrl}/item/atualizar-quantidade/`,
        {
          pedido_id: pedidoId,
          produto_id: produtoId,
          quantidade: quantidade
        },
        csrfToken
      );
      return response;
    } catch (error) {
      console.error('Erro ao atualizar quantidade:', error);
      throw error;
    }
  }

  /**
   * Finaliza um pedido
   */
  async finalizarPedido(pedidoId, csrfToken) {
    try {
      const response = await apiService.post(
        `${this.baseUrl}/${pedidoId}/finalizar/`,
        {},
        csrfToken
      );
      return response;
    } catch (error) {
      console.error('Erro ao finalizar pedido:', error);
      throw error;
    }
  }

  /**
   * Processa pagamento
   */
  async processarPagamento(pedidoId, metodoPagamento, csrfToken) {
    try {
      const response = await apiService.post(
        `${this.baseUrl}/processar-pagamento/`,
        {
          pedido_id: pedidoId,
          metodo_pagamento: metodoPagamento
        },
        csrfToken
      );
      return response;
    } catch (error) {
      console.error('Erro ao processar pagamento:', error);
      throw error;
    }
  }

  /**
   * Cancela um pedido
   */
  async cancelarPedido(pedidoId, motivo = '', csrfToken) {
    try {
      const response = await apiService.post(
        `${this.baseUrl}/${pedidoId}/cancelar/`,
        { motivo },
        csrfToken
      );
      return response;
    } catch (error) {
      console.error('Erro ao cancelar pedido:', error);
      throw error;
    }
  }

  /**
   * Obtém detalhes de um pedido
   */
  async obterPedido(pedidoId) {
    try {
      const response = await apiService.get(`${this.baseUrl}/${pedidoId}/`);
      return response;
    } catch (error) {
      console.error('Erro ao obter pedido:', error);
      throw error;
    }
  }

  /**
   * Lista pedidos do cliente
   */
  async listarPedidosCliente(status = null) {
    try {
      const url = status 
        ? `${this.baseUrl}/meus-pedidos/?status=${status}`
        : `${this.baseUrl}/meus-pedidos/`;
      
      const response = await apiService.get(url);
      return response;
    } catch (error) {
      console.error('Erro ao listar pedidos:', error);
      throw error;
    }
  }

  /**
   * Obtém pedido ativo do cliente (status = 0 - Fazendo pedido)
   */
  async obterPedidoAtivo() {
    try {
      const response = await this.listarPedidosCliente('0');
      if (response.success && response.pedidos && response.pedidos.length > 0) {
        // Retorna o primeiro pedido ativo encontrado
        const pedidoAtivo = response.pedidos[0];
        return await this.obterPedido(pedidoAtivo.id);
      }
      return null;
    } catch (error) {
      console.error('Erro ao obter pedido ativo:', error);
      return null;
    }
  }

  /**
   * Cria ou obtém pedido ativo para adicionar itens
   */
  async obterOuCriarPedidoAtivo(csrfToken) {
    try {
      // Primeiro tenta obter pedido ativo
      let pedidoAtivo = await this.obterPedidoAtivo();
      
      if (!pedidoAtivo) {
        // Se não existe, cria um novo
        const novoPedido = await this.criarPedido({
          delivery_address: '',
          notes: ''
        }, csrfToken);
        
        if (novoPedido.success) {
          pedidoAtivo = await this.obterPedido(novoPedido.pedido_id);
        }
      }
      
      return pedidoAtivo;
    } catch (error) {
      console.error('Erro ao obter ou criar pedido ativo:', error);
      throw error;
    }
  }
}

// Instância singleton
export const pedidoService = new PedidoService();
export default pedidoService;