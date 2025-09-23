# Templates do App Pedido - Cliente

Esta pasta contém os templates HTML para o frontend do cliente no app de pedidos.

## Estrutura de Arquivos

```
apps/pedido/templates/client/
├── base.html                   # Template base com navegação e layout comum
├── status_pedido.html          # Status do pedido atual
├── historico_pedidos.html      # Histórico de pedidos do usuário
├── checkout.html               # Finalização do pedido
└── detalhes_pedido.html        # Detalhes de um pedido específico
```

## Descrição dos Templates

### 1. base.html
Template base que contém:
- Estrutura HTML comum
- Navegação principal
- Estilos CSS base
- Scripts JavaScript utilitários
- Sistema de mensagens
- Footer

### 2. status_pedido.html
Página para acompanhar o status do pedido atual:
- Timeline visual do progresso do pedido
- Detalhes dos itens
- Informações de entrega
- Atualização automática a cada 30 segundos
- Opções para cancelar (quando aplicável)

### 3. historico_pedidos.html
Lista todos os pedidos do usuário:
- Filtros por status e data
- Cards com resumo de cada pedido
- Paginação
- Ações contextuais (repetir pedido, avaliar, etc.)
- Estado vazio quando não há pedidos

### 4. checkout.html
Página de finalização do pedido:
- Seleção de tipo de entrega (delivery/retirada)
- Gerenciamento de endereços
- Métodos de pagamento
- Resumo do carrinho com controles de quantidade
- Validações de formulário
- Máscaras para campos (CEP, cartão, etc.)

### 5. detalhes_pedido.html
Visualização detalhada de um pedido específico:
- Timeline completa do pedido
- Informações do cliente
- Tabela detalhada dos itens
- Cálculo de totais
- Ações contextuais por status

## Funcionalidades Implementadas

### Interface do Usuário
- Design responsivo para mobile e desktop
- Navegação intuitiva entre páginas
- Feedback visual para diferentes status
- Máscaras de entrada para campos especiais

### Interatividade
- Controles de quantidade no checkout
- Filtros dinâmicos no histórico
- Seleção de endereços e métodos de pagamento
- Confirmações para ações críticas

### Status e Estados
- Sistema de badges coloridos para diferentes status
- Timeline visual do progresso
- Tratamento de estados vazios
- Mensagens informativas

## Integração com Django

### Context Variables Esperadas
- `pedido`: Objeto do pedido atual
- `pedidos`: QuerySet de pedidos (para histórico)
- `cliente`: Objeto do cliente logado
- `messages`: Sistema de mensagens do Django

### URLs Esperadas
- `pedido:status`: Status do pedido atual
- `pedido:historico`: Histórico de pedidos
- `pedido:checkout`: Finalização do pedido
- `pedido:detalhes`: Detalhes de um pedido específico
- `produto:cardapio`: Cardápio de produtos
- `cliente:perfil`: Perfil do cliente

### Form Handling
Os templates incluem estruturas para:
- Formulários de endereço
- Dados de pagamento
- Filtros de busca
- Controles de quantidade

## Próximos Passos

Para implementar completamente:

1. **Views**: Criar as views correspondentes em `apps/pedido/views.py`
2. **URLs**: Configurar as rotas em `apps/pedido/urls.py`
3. **JavaScript**: Implementar as funções AJAX para:
   - Atualização de quantidades
   - Cancelamento de pedidos
   - Filtros dinâmicos
   - Validações em tempo real
4. **CSS**: Considerar usar um framework CSS ou personalizar mais os estilos
5. **Validações**: Implementar validações do lado servidor
6. **Testes**: Criar testes para as views e templates

## Notas Técnicas

- Templates usam Django Template Language
- Estilos CSS inline para simplicidade (pode ser externalizado)
- JavaScript vanilla (pode ser migrado para framework se necessário)
- Design mobile-first responsivo
- Acessibilidade básica implementada
- SEO-friendly com títulos e meta tags apropriados