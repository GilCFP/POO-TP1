import { useState, useCallback, useContext, createContext } from 'react';
import { pedidoService } from '../services/pedidoService';
import { AuthUtils } from '@shared/services/api';

/**
 * Context para compartilhar estado do carrinho entre componentes
 */
const CarrinhoContext = createContext();

/**
 * Provider do contexto do carrinho
 */
export const CarrinhoProvider = ({ children, csrfToken }) => {
  const [pedidoAtivo, setPedidoAtivo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const value = {
    pedidoAtivo,
    setPedidoAtivo,
    loading,
    setLoading,
    error,
    setError,
    csrfToken
  };

  return (
    <CarrinhoContext.Provider value={value}>
      {children}
    </CarrinhoContext.Provider>
  );
};

/**
 * Hook para gerenciar carrinho de compras
 */
export const useCarrinho = () => {
  const context = useContext(CarrinhoContext);
  
  if (!context) {
    throw new Error('useCarrinho deve ser usado dentro de CarrinhoProvider');
  }

  const {
    pedidoAtivo,
    setPedidoAtivo,
    loading,
    setLoading,
    error,
    setError,
    csrfToken
  } = context;

  /**
   * Carrega pedido ativo
   */
  const carregarPedidoAtivo = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const pedido = await pedidoService.obterPedidoAtivo();
      setPedidoAtivo(pedido);
      
      return pedido;
    } catch (err) {
      setError(err.message);
      console.error('Erro ao carregar pedido ativo:', err);
      return null;
    } finally {
      setLoading(false);
    }
  }, [setPedidoAtivo, setLoading, setError]);

  /**
   * Adiciona produto ao carrinho
   */
  const adicionarProduto = useCallback(async (produtoId, quantidade = 1, instrucoesEspeciais = '') => {
    try {
      setLoading(true);
      setError(null);

      // Verifica se usuário está autenticado
      const isAuthenticated = AuthUtils.isAuthenticated();
      if (!isAuthenticated) {
        // Redireciona para login
        const currentUrl = window.location.pathname;
        window.location.href = `/clientes/login/?next=${encodeURIComponent(currentUrl)}`;
        return {
          success: false,
          error: 'É necessário fazer login para adicionar produtos ao carrinho',
          redirect: true
        };
      }

      // Obtém ou cria pedido ativo
      let pedido = pedidoAtivo;
      if (!pedido) {
        pedido = await pedidoService.obterOuCriarPedidoAtivo(csrfToken);
        if (!pedido) {
          throw new Error('Não foi possível criar pedido');
        }
        setPedidoAtivo(pedido);
      }

      // Adiciona item ao pedido
      const response = await pedidoService.adicionarItem(
        pedido.pedido.id,
        produtoId,
        quantidade,
        instrucoesEspeciais,
        csrfToken
      );

      if (response.success) {
        // Atualiza pedido local
        await carregarPedidoAtivo();
        return {
          success: true,
          message: response.message || 'Produto adicionado com sucesso!',
          item: response.item
        };
      } else {
        throw new Error(response.error || 'Erro ao adicionar produto');
      }
    } catch (err) {
      setError(err.message);
      console.error('Erro ao adicionar produto:', err);
      return {
        success: false,
        error: err.message
      };
    } finally {
      setLoading(false);
    }
  }, [pedidoAtivo, setPedidoAtivo, carregarPedidoAtivo, csrfToken, setLoading, setError]);

  /**
   * Remove produto do carrinho
   */
  const removerProduto = useCallback(async (produtoId) => {
    if (!pedidoAtivo) return;

    try {
      setLoading(true);
      setError(null);

      const response = await pedidoService.removerItem(
        pedidoAtivo.pedido.id,
        produtoId,
        csrfToken
      );

      if (response.success) {
        await carregarPedidoAtivo();
        return {
          success: true,
          message: response.message || 'Produto removido com sucesso!'
        };
      } else {
        throw new Error(response.error || 'Erro ao remover produto');
      }
    } catch (err) {
      setError(err.message);
      console.error('Erro ao remover produto:', err);
      return {
        success: false,
        error: err.message
      };
    } finally {
      setLoading(false);
    }
  }, [pedidoAtivo, carregarPedidoAtivo, csrfToken, setLoading, setError]);

  /**
   * Atualiza quantidade de produto
   */
  const atualizarQuantidade = useCallback(async (produtoId, novaQuantidade) => {
    if (!pedidoAtivo) return;

    try {
      setLoading(true);
      setError(null);

      const response = await pedidoService.atualizarQuantidadeItem(
        pedidoAtivo.pedido.id,
        produtoId,
        novaQuantidade,
        csrfToken
      );

      if (response.success) {
        await carregarPedidoAtivo();
        return {
          success: true,
          message: response.message || 'Quantidade atualizada com sucesso!'
        };
      } else {
        throw new Error(response.error || 'Erro ao atualizar quantidade');
      }
    } catch (err) {
      setError(err.message);
      console.error('Erro ao atualizar quantidade:', err);
      return {
        success: false,
        error: err.message
      };
    } finally {
      setLoading(false);
    }
  }, [pedidoAtivo, carregarPedidoAtivo, csrfToken, setLoading, setError]);

  /**
   * Finaliza pedido
   */
  const finalizarPedido = useCallback(async () => {
    if (!pedidoAtivo) return;

    try {
      setLoading(true);
      setError(null);

      const response = await pedidoService.finalizarPedido(
        pedidoAtivo.pedido.id,
        csrfToken
      );

      if (response.success) {
        setPedidoAtivo(null); // Limpa pedido ativo
        return {
          success: true,
          message: response.message || 'Pedido finalizado com sucesso!',
          pedido: response.pedido
        };
      } else {
        throw new Error(response.error || 'Erro ao finalizar pedido');
      }
    } catch (err) {
      setError(err.message);
      console.error('Erro ao finalizar pedido:', err);
      return {
        success: false,
        error: err.message
      };
    } finally {
      setLoading(false);
    }
  }, [pedidoAtivo, setPedidoAtivo, csrfToken, setLoading, setError]);

  /**
   * Cancela pedido
   */
  const cancelarPedido = useCallback(async (motivo = '') => {
    if (!pedidoAtivo) return;

    try {
      setLoading(true);
      setError(null);

      const response = await pedidoService.cancelarPedido(
        pedidoAtivo.pedido.id,
        motivo,
        csrfToken
      );

      if (response.success) {
        setPedidoAtivo(null); // Limpa pedido ativo
        return {
          success: true,
          message: response.message || 'Pedido cancelado com sucesso!'
        };
      } else {
        throw new Error(response.error || 'Erro ao cancelar pedido');
      }
    } catch (err) {
      setError(err.message);
      console.error('Erro ao cancelar pedido:', err);
      return {
        success: false,
        error: err.message
      };
    } finally {
      setLoading(false);
    }
  }, [pedidoAtivo, setPedidoAtivo, csrfToken, setLoading, setError]);

  /**
   * Calcula total de itens no carrinho
   */
  const totalItens = pedidoAtivo?.pedido?.itens?.reduce((total, item) => total + item.quantidade, 0) || 0;

  /**
   * Calcula valor total do carrinho
   */
  const valorTotal = pedidoAtivo?.pedido?.total || 0;

  /**
   * Verifica se carrinho está vazio
   */
  const carrinhoVazio = totalItens === 0;

  return {
    // Estado
    pedidoAtivo,
    loading,
    error,
    totalItens,
    valorTotal,
    carrinhoVazio,
    
    // Ações
    carregarPedidoAtivo,
    adicionarProduto,
    removerProduto,
    atualizarQuantidade,
    finalizarPedido,
    cancelarPedido,
    
    // Utilidades
    setError,
    clearError: () => setError(null)
  };
};