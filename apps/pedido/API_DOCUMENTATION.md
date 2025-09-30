# API de Pedidos - Documentação

Esta documentação descreve as rotas da API implementadas para o sistema de pedidos.

## Estrutura de Resposta

Todas as respostas da API seguem o padrão:

```json
{
    "success": true/false,
    "message": "Mensagem descritiva",
    "data": {...},  // dados específicos da operação
    "error": "Mensagem de erro (apenas quando success=false)"
}
```

## Rotas do Cliente

### 1. Criar Pedido
- **POST** `/pedido/api/criar/`
- **Body**:
```json
{
    "client_id": 1,  // opcional se cliente autenticado
    "delivery_address": "Rua X, 123",
    "notes": "Observações especiais"
}
```

### 2. Adicionar Item ao Pedido
- **POST** `/pedido/api/item/adicionar/`
- **Body**:
```json
{
    "pedido_id": 1,
    "produto_id": 5,
    "quantidade": 2,
    "instrucoes_especiais": "Sem cebola"
}
```

### 3. Remover Item do Pedido
- **POST** `/pedido/api/item/remover/`
- **Body**:
```json
{
    "pedido_id": 1,
    "produto_id": 5
}
```

### 4. Atualizar Quantidade de Item
- **POST** `/pedido/api/item/atualizar-quantidade/`
- **Body**:
```json
{
    "pedido_id": 1,
    "produto_id": 5,
    "quantidade": 3  // 0 para remover
}
```

### 5. Finalizar Pedido
- **POST** `/pedido/api/{pedido_id}/finalizar/`
- Move o pedido para status "Aguardando Pagamento"

### 6. Processar Pagamento
- **POST** `/pedido/api/processar-pagamento/`
- **Body**:
```json
{
    "pedido_id": 1,
    "metodo_pagamento": "cartao"  // opcional
}
```

### 7. Cancelar Pedido
- **POST** `/pedido/api/{pedido_id}/cancelar/`
- **Body**:
```json
{
    "motivo": "Mudança de planos"
}
```

### 8. Obter Detalhes do Pedido
- **GET** `/pedido/api/{pedido_id}/`
- Retorna informações completas do pedido

### 9. Listar Pedidos do Cliente
- **GET** `/pedido/api/meus-pedidos/`
- **Query Params**: `?status=pending` (opcional)

## Rotas do Restaurante (prefixo _)

### 1. Atualizar Status do Pedido
- **POST** `/pedido/api/_pedido/{pedido_id}/atualizar-status/`
- **Body**:
```json
{
    "status": "3",  // código do status
    "observacoes": "Preparação iniciada",
    "usuario": "João (Cozinha)"
}
```

### 2. Avançar Status Automaticamente
- **POST** `/pedido/api/_pedido/{pedido_id}/avancar-status/`
- **Body**:
```json
{
    "usuario": "Sistema"
}
```

### 3. Obter Detalhes Completos do Pedido
- **GET** `/pedido/api/_pedido/{pedido_id}/detalhes/`
- Retorna pedido + histórico + estatísticas

### 4. Obter Estatísticas do Pedido
- **GET** `/pedido/api/_pedido/{pedido_id}/estatisticas/`
- Retorna informações nutricionais e outras estatísticas

### 5. Listar Pedidos por Status
- **GET** `/pedido/api/_pedidos/por-status/?status=2`
- **Query Params**: `status` (obrigatório)

## Status dos Pedidos

| Código | Nome | Descrição |
|--------|------|-----------|
| -1 | Cancelado | Pedido cancelado |
| 0 | Fazendo pedido | Cliente montando o pedido |
| 1 | Aguardando pagamento | Pedido finalizado, aguardando pagamento |
| 2 | Aguardando | Pagamento processado, na fila |
| 3 | Preparando | Em preparação na cozinha |
| 4 | Pronto | Pronto para entrega/retirada |
| 5 | Sendo entregue | Em transporte |
| 6 | Entregue | Entregue ao cliente |

## Códigos de Erro HTTP

- **400**: Bad Request - Dados inválidos ou malformados
- **401**: Unauthorized - Cliente não autenticado
- **404**: Not Found - Recurso não encontrado
- **500**: Internal Server Error - Erro interno do servidor

## Autenticação

As rotas do cliente requerem autenticação via middleware. O sistema verifica:
- Se `request.is_client_authenticated` é `True`
- Se `request.client` contém os dados do cliente

As rotas do restaurante (prefixo `_`) requerem autenticação específica do restaurante (a ser implementada).

## Validações Implementadas

### Cliente
- Verificação de propriedade do pedido
- Validação de status para modificações
- Verificação de dados obrigatórios

### Restaurante
- Validação de status válidos
- Verificação de transições de status permitidas
- Logging de todas as alterações no histórico

## Exemplos de Uso

### Fluxo Completo do Cliente

1. **Criar pedido**:
```bash
curl -X POST /pedido/api/criar/ \
  -H "Content-Type: application/json" \
  -d '{"delivery_address": "Rua A, 123", "notes": "Sem cebola"}'
```

2. **Adicionar itens**:
```bash
curl -X POST /pedido/api/item/adicionar/ \
  -H "Content-Type: application/json" \
  -d '{"pedido_id": 1, "produto_id": 5, "quantidade": 2}'
```

3. **Finalizar pedido**:
```bash
curl -X POST /pedido/api/1/finalizar/
```

4. **Processar pagamento**:
```bash
curl -X POST /pedido/api/processar-pagamento/ \
  -H "Content-Type: application/json" \
  -d '{"pedido_id": 1, "metodo_pagamento": "cartao"}'
```

### Fluxo do Restaurante

1. **Avançar status**:
```bash
curl -X POST /pedido/api/_pedido/1/avancar-status/ \
  -H "Content-Type: application/json" \
  -d '{"usuario": "João"}'
```

2. **Ver detalhes**:
```bash
curl -X GET /pedido/api/_pedido/1/detalhes/
```