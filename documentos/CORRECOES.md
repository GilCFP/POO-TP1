# Checklist de Correções - POO TP1

## 1. ENCAPSULAMENTO - Classes/

### Produto.py
- [x] Atributos privados: `_nome`, `_preco`, `_disponivel`, `_descricao`, `_tempo_preparo`
- [x] Propriedades para acesso controlado: `nome`, `preco`, `disponivel`
- [x] Setters com validação (preço > 0, disponibilidade booleana)
- [x] Método `aplicar_desconto()` com validação

### Alimento.py
- [x] Herança de Produto
- [x] Atributos privados: `_data_expiracao`, `_calorias`, `_tempo_preparo`, `_ingredientes`, `_restricoes_alimentares`
- [x] Propriedades: `calorias`, `ingredientes`, `restricoes_alimentares`
- [x] Métodos: `adicionar_ingrediente()`, `remover_ingrediente()`

### Comida.py
- [x] Herança de Alimento
- [x] Atributo privado: `_tipo_comida`
- [x] Propriedade: `tipo_comida`
- [x] Implementa `validar()` abstrato

### Bebida.py
- [x] Herança de Alimento
- [x] Atributo privado: `_volume_ml`, `_alcoolica`
- [x] Propriedades: `volume_ml`, `alcoolica`
- [x] Implementa `validar()` abstrato

### Combo.py
- [x] Agregação de Produtos
- [x] Atributos privados: `_produtos`, `_desconto_combo`
- [x] Propriedades: `produtos`, `desconto_combo`
- [x] Métodos: `adicionar_produto()`, `remover_produto()`, `calcular_total()`

### Cliente.py
- [x] Atributos privados: `_cpf`, `_nome`, `_email`, `_telefone`, `_saldo`, `_historico_pedidos`, `_restricoes_alimentares`
- [x] Propriedades: `cpf`, `nome`, `email`, `telefone`, `saldo`, `historico_pedidos`
- [x] Métodos: `adicionar_fundo()`, `remover_fundo()` com validações
- [x] Validações em __init__ (CPF, email, saldo inicial)

### Pedido.py
- [x] Atributos privados: `_itens`, `_total`, `_status`, `_cliente`, `_data_pedido`
- [x] Propriedades: `itens`, `total`, `status`, `cliente`, `data_pedido`
- [x] Métodos: `adicionar_item()`, `remover_item()`, `mudar_status()`
- [x] Validações: Total recalculado, transições de status validadas

### Cozinha.py
- [x] Atributos privados: `_pedidos_em_progresso`, `_fila_pedidos`, `_capacidade_maxima`, `_tempo_medio_preparo`
- [x] Propriedades: `pedidos_em_progresso`, `fila_pedidos`, `capacidade_maxima`
- [x] Métodos: `adicionar_pedido()`, `iniciar_preparo()`, `finalizar_pedido()`, `esta_cheia()`
- [x] Validações: Capacidade respeitada, status transições validadas

### Caixa.py
- [x] Atributos privados: `_total_receita`, `_historico_transacoes`
- [x] Propriedades: `total_receita`, `historico_transacoes`
- [x] Método: `processar_pagamento()` com validação de saldo

### Restaurante.py
- [x] Atributos privados: `_menu`, `_clientes`, `_caixa`, `_cozinha`
- [x] Propriedades: `menu`, `clientes`, `caixa`, `cozinha`
- [x] Métodos: `obter_produto_por_nome()`, `obter_cliente_por_nome()`, `registrar_cliente()`
- [x] Validações: Produtos duplicados, clientes duplicados

---

## 2. CLASSE ABSTRATA

### EntidadeBase.py (NOVO)
- [x] Classe abstrata com `from abc import ABC, abstractmethod`
- [x] Atributos protegidos: `_id`, `_data_criacao`
- [x] Método abstrato: `validar() -> bool`
- [x] Todas as 11 classes de negócio herdam de EntidadeBase
- [x] Todas as 11 classes implementam `validar()`

**Verificação de herança:**
```
EntidadeBase (abstrato)
├── Produto
│   ├── Alimento
│   │   ├── Comida
│   │   └── Bebida
│   └── Combo
├── Cliente
├── Pedido
├── Cozinha
├── Caixa
└── Restaurante
```

---

## 3. DOCUMENTAÇÃO

### Todas as classes em Classes/
- [x] Docstring de classe (descrição, responsabilidade, exemplo de uso)
- [x] Type hints completos em parâmetros e retornos
- [x] Docstrings em todos os métodos públicos
- [x] Exemplos de código nas docstrings

**Exemplo de padrão:**
```python
class Produto(EntidadeBase):
    """Classe que representa um produto genérico.
    
    Responsabilidades:
    - Manter informações do produto (nome, preço)
    - Validar dados de entrada
    - Permitir aplicação de descontos
    
    Exemplo de uso:
        >>> produto = Produto("Pizza", 35.00)
        >>> produto.preco = 31.50  # Com desconto
    """
    
    def aplicar_desconto(self, percentual: float) -> None:
        """Aplica desconto ao produto.
        
        Args:
            percentual: Percentual de desconto (0-100)
            
        Raises:
            ValueError: Se percentual inválido
        """
```

---

## 4. ORGANIZAÇÃO DE ARQUIVOS

### Antes
```
POO-TP1/
├── Produto.py (raiz)
├── Cliente.py (raiz)
├── Pedido.py (raiz)
... (11 arquivos na raiz)
```

### Depois
```
POO-TP1/
├── Classes/
│   ├── EntidadeBase.py (NOVO)
│   ├── Produto.py
│   ├── Alimento.py
│   ├── Comida.py
│   ├── Bebida.py
│   ├── Combo.py
│   ├── Cliente.py
│   ├── Pedido.py
│   ├── Cozinha.py
│   ├── Caixa.py
│   ├── Restaurante.py
│   ├── StatusPedido.py
│   └── RestricaoAlimentar.py
├── documentos/
│   ├── GUIA_PROFESSORA.md
│   ├── CORRECOES.md (este arquivo)
│   ├── NOVA_ARQUITETURA.md
│   ├── README_ARQUITETURA.md
│   └── README_SCRIPTS.md
```

---

## 5. VALIDAÇÕES IMPLEMENTADAS

### Produto
- Preço deve ser > 0
- Nome não pode ser vazio
- Disponibilidade deve ser booleana

### Cliente
- CPF válido (11 dígitos)
- Email válido
- Saldo inicial >= 0

### Pedido
- Não permite itens duplicados
- Total recalculado automaticamente
- Transições de status validadas

### Cozinha
- Não excedem capacidade máxima
- Pedidos em fila com status validado
- Transições de status respeitadas

### Caixa
- Saldo do cliente suficiente para pagamento
- Histórico de transações mantido



## 6. COMO VALIDAR

### Encapsulamento
1. Abra: `Classes/Cliente.py`
2. Procure por: `@property` (deve haver ~5-7)
3. Procure por: `@property.setter` (deve haver ~3-5)
4. Procure por: atributos privados `_cpf`, `_nome`, `_saldo`

### Classe Abstrata
1. Abra: `Classes/EntidadeBase.py`
2. Procure por: `@abstractmethod`
3. Procure por: `class X(EntidadeBase):`
4. Verifique: `def validar(self) -> bool:`

### Documentação
1. Abra: Qualquer classe em `Classes/`
2. Procure por: `"""` (docstring no topo)
3. Procure por: `->` em assinaturas (type hints)
4. Procure por: `Args:` e `Returns:` em métodos

### Organização
1. Verifique: Pasta `Classes/` existe e contém 13 arquivos
2. Verifique: Pasta `documentos/` existe
3. Verifique: Arquivos antigos na raiz foram removidos/movidos

---