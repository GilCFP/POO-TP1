# Frontend - Integração com API de Pedidos

Esta documentação explica como usar os componentes React implementados para integrar com a API de pedidos.

## Arquitetura

O frontend segue a estrutura do webpack com separação por apps e escopos:

```
frontend/src/apps/
├── pedido/
│   ├── client/           # Componentes para clientes
│   ├── shared/          # Componentes/serviços compartilhados
│   └── admin/           # Componentes administrativos
├── produto/
│   ├── client/          # Componentes para visualização de produtos
│   └── shared/
└── shared/              # Recursos globais
```

## Serviços Implementados

### PedidoService (`/apps/pedido/shared/services/pedidoService.js`)

Serviço principal para comunicação com a API de pedidos:

```javascript
import pedidoService from '@pedido/shared/services/pedidoService';

// Criar pedido
const pedido = await pedidoService.criarPedido(dadosPedido, csrfToken);

// Adicionar item
const response = await pedidoService.adicionarItem(
  pedidoId, 
  produtoId, 
  quantidade, 
  instrucoesEspeciais, 
  csrfToken
);

// Finalizar pedido
const finalizacao = await pedidoService.finalizarPedido(pedidoId, csrfToken);
```

### Hook useCarrinho (`/apps/pedido/shared/hooks/useCarrinho.js`)

Hook React para gerenciar estado do carrinho:

```javascript
import { useCarrinho, CarrinhoProvider } from '@pedido/shared/hooks/useCarrinho';

// No componente pai
<CarrinhoProvider csrfToken={csrfToken}>
  <MeuComponente />
</CarrinhoProvider>

// No componente filho
const { pedidoAtivo, adicionarProduto, loading } = useCarrinho();
```

## Componentes Principais

### 1. AdicionarCarrinhoButton

Botão para adicionar produtos ao pedido com feedback visual.

**Localização:** `/apps/produto/client/components/AdicionarCarrinhoButton.jsx`

**Uso:**
```jsx
import AdicionarCarrinhoButton from '../components/AdicionarCarrinhoButton';

<AdicionarCarrinhoButton
  produto={produto}
  onSuccess={(resultado) => console.log('Adicionado!', resultado)}
  onError={(erro) => console.error('Erro:', erro)}
/>
```

**Props:**
- `produto`: Objeto do produto com id, name, price
- `quantidade`: Quantidade inicial (padrão: 1)
- `className`: Classes CSS adicionais
- `disabled`: Desabilita o botão
- `onSuccess`: Callback de sucesso
- `onError`: Callback de erro

### 2. CarrinhoIndicador

Indicador flutuante mostrando o estado atual do carrinho.

**Localização:** `/apps/pedido/client/components/CarrinhoIndicador.jsx`

**Uso:**
```jsx
import CarrinhoIndicador from '@pedido/client/components/CarrinhoIndicador';

<CarrinhoIndicador 
  onViewCarrinho={(pedidoAtivo) => window.location.href = '/checkout/'}
  showTotal={true}
  showItemCount={true}
/>
```

**Props:**
- `showTotal`: Mostra valor total (padrão: true)
- `showItemCount`: Mostra contador de itens (padrão: true)
- `onViewCarrinho`: Callback ao clicar no indicador
- `className`: Classes CSS adicionais

### 3. ProdutoApp

Componente principal para listagem de produtos com integração ao carrinho.

**Localização:** `/apps/produto/client/home/ProdutoApp.jsx`

**Uso:**
```jsx
// Renderizado automaticamente pelo Django template
// Dados dos produtos carregados via elemento DOM
```

**Funcionalidades:**
- Lista produtos disponíveis
- Integração com botão "Adicionar ao Carrinho"
- Indicador de carrinho flutuante
- Feedback de ações do usuário

### 4. CheckoutApp

Componente para finalização do pedido.

**Localização:** `/apps/pedido/client/checkout/CheckoutApp.jsx`

**Funcionalidades:**
- Resumo do pedido
- Opções de entrega
- Seleção de pagamento
- Finalização e processamento

### 5. StatusApp

Componente para acompanhamento do pedido.

**Localização:** `/apps/pedido/client/status/StatusApp.jsx`

**Funcionalidades:**
- Exibe status atual do pedido
- Atualização automática a cada 30 segundos
- Histórico de mudanças de status

## Fluxo de Uso Completo

### 1. Visualização de Produtos
```jsx
// Em produto/client/home/ProdutoApp.jsx
<CarrinhoProvider csrfToken={csrfToken}>
  <div className="product-grid">
    {produtos.map(produto => (
      <div key={produto.id} className="product-card">
        <h2>{produto.name}</h2>
        <p>R$ {produto.price}</p>
        <AdicionarCarrinhoButton 
          produto={produto}
          onSuccess={handleAdicionado}
          onError={handleErro}
        />
      </div>
    ))}
  </div>
  <CarrinhoIndicador onViewCarrinho={goToCheckout} />
</CarrinhoProvider>
```

### 2. Adição de Produtos
```javascript
// Fluxo interno do AdicionarCarrinhoButton
const handleAdicionarAoPedido = async () => {
  // 1. Obtém ou cria pedido ativo
  const pedidoAtivo = await pedidoService.obterOuCriarPedidoAtivo(csrfToken);
  
  // 2. Adiciona item ao pedido
  const response = await pedidoService.adicionarItem(
    pedidoAtivo.pedido.id,
    produto.id,
    quantidade,
    instrucoesEspeciais,
    csrfToken
  );
  
  // 3. Atualiza estado local via useCarrinho
  // 4. Mostra feedback visual
};
```

### 3. Checkout
```javascript
// No CheckoutApp
const finalizarPedido = async (formData) => {
  // 1. Finaliza pedido (status: aguardando pagamento)
  const finalizeResponse = await pedidoService.finalizarPedido(pedido.id, csrfToken);
  
  // 2. Processa pagamento
  const paymentResponse = await pedidoService.processarPagamento(
    pedido.id, 
    metodoPagamento, 
    csrfToken
  );
  
  // 3. Redireciona para status
  window.location.href = `/pedido/${pedido.id}/status/`;
};
```

### 4. Acompanhamento
```javascript
// No StatusApp
useEffect(() => {
  // Auto-refresh a cada 30 segundos
  const interval = setInterval(() => {
    fetchPedidoStatus(pedido.id);
  }, 30000);
  
  return () => clearInterval(interval);
}, [pedido]);
```

## Estilos CSS

### Temas e Cores Principais
- **Primário:** `#ff6b35` (laranja vibrante)
- **Sucesso:** `#28a745` (verde)
- **Erro:** `#dc3545` (vermelho)
- **Cinza:** `#6c757d`

### Classes CSS Úteis
```css
/* Botões */
.adicionar-carrinho-btn          /* Botão padrão */
.adicionar-carrinho-btn.loading  /* Estado carregando */
.adicionar-carrinho-btn.success  /* Estado sucesso */
.adicionar-carrinho-btn.error    /* Estado erro */

/* Carrinho Indicador */
.carrinho-indicador              /* Container principal */
.carrinho-indicador-button       /* Botão do indicador */
.item-count                      /* Contador de itens */

/* Status do Pedido */
.status-cancelled                /* Cancelado */
.status-pending                  /* Aguardando pagamento */
.status-preparing               /* Preparando */
.status-ready                   /* Pronto */
.status-delivered               /* Entregue */
```

## Configuração e Deploy

### 1. Webpack Aliases
```javascript
// webpack.config.js
resolve: {
  alias: {
    '@pedido': path.resolve(__dirname, 'src/apps/pedido'),
    '@produto': path.resolve(__dirname, 'src/apps/produto'),
    '@shared': path.resolve(__dirname, 'src/shared'),
    '@components': path.resolve(__dirname, 'src/shared/components')
  }
}
```

### 2. Django Template Integration
```html
<!-- base.html -->
{{ csrf_token }}
<script id="produtos-data" type="application/json">
  {{ produtos_json|safe }}
</script>
```

### 3. CSRF Token
```javascript
// Método para obter CSRF token
const getCSRFToken = () => {
  const token = document.querySelector('[name=csrfmiddlewaretoken]');
  return token ? token.value : null;
};
```

## Debugging e Logs

### Console Logs Úteis
```javascript
// No PedidoService
console.log('Pedido criado:', response);
console.log('Item adicionado:', item);
console.error('Erro na API:', error);

// No useCarrinho
console.log('Estado do carrinho:', pedidoAtivo);
console.log('Ação executada:', resultado);
```

### Verificação de Estado
```javascript
// Verificar pedido ativo
const pedido = pedidoService.getCurrentPedido();
console.log('Pedido atual:', pedido);

// Verificar listeners
console.log('Listeners registrados:', pedidoService.listeners.length);
```

## Extensões Futuras

### 1. WebSocket para Updates em Tempo Real
```javascript
// Integração com WebSocket para status do pedido
const socket = new WebSocket('ws://localhost:8000/ws/pedido/');
socket.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'status_update') {
    updatePedidoStatus(data.pedido);
  }
};
```

### 2. Cache Local
```javascript
// localStorage para cache de pedidos
const cacheKey = `pedido_${pedidoId}`;
localStorage.setItem(cacheKey, JSON.stringify(pedidoData));
```

### 3. PWA Support
```javascript
// Service Worker para funcionalidade offline
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js');
}
```