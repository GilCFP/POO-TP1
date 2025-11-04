# Guia da Professora - POO TP1

## Introdução

Este documento orienta sobre a estrutura do projeto, navegação de pastas e verificação das correções implementadas.

## Estrutura de Pastas

### 1. **Classes/** - Domínio da Aplicação
Contém as 13 classes Python que implementam a lógica de negócio do sistema. Todas herdam de `EntidadeBase` (classe abstrata).

**Arquivo crítico:** `EntidadeBase.py` - Define o contrato abstrato que todas as demais classes implementam.

### 2. **apps/** - Integração Django
Aplicações Django que interagem com as classes do domínio:
- `cliente/` - Gerenciamento de clientes
- `produto/` - Catálogo de produtos
- `pedido/` - Sistema de pedidos
- `restaurante/` - Operações principais

### 3. **documentos/** - Referência Técnica
- `CORRECOES.md` - Checklist completo do que foi corrigido
- `NOVA_ARQUITETURA.md` - Propostas de melhoria arquitetônica
- `README_ARQUITETURA.md` - Análise da arquitetura atual
- `README_SCRIPTS.md` - Scripts de utilitário disponíveis

### 4. **frontend/** - Interface React
Camada de apresentação em React (integração com backend Django).

## Critérios de Avaliação - O que foi Corrigido

### ✓ Encapsulamento
**Onde:** `Classes/` (todas as classes)

Todas as classes implementam encapsulamento através de:
- Atributos privados (prefixo `_`)
- Propriedades com `@property` e `@property.setter`
- Validações em setters

**Exemplos:**
- `Produto.py` - Propriedades: `nome`, `preco`, `disponivel`
- `Cliente.py` - Propriedades: `saldo`, `cpf`, `nome`
- `Pedido.py` - Propriedades: `itens`, `total`, `status`

### ✓ Classe Abstrata
**Onde:** `Classes/EntidadeBase.py`

Classe abstrata base que define contrato para todas as entidades:
- Método abstrato `validar()` que deve ser implementado por cada subclasse
- Atributos comuns: `_id`, `_data_criacao`
- Todas as 11 classes de negócio herdam e implementam `validar()`

**Implementação:** Usa módulo `abc` do Python com decoradores `@abstractmethod`

### ✓ Documentação
**Onde:** `Classes/` (todas as classes)

Cada classe possui:
- **Docstring de classe** - Descrição da responsabilidade
- **Type hints** - Tipagem em todos os métodos e atributos
- **Docstrings de método** - Explicação de cada operação
- **Exemplos de uso** - Código demonstrativo em cada classe

**Verificação:** Abra qualquer classe e veja seções de documentação

### ✓ Organização de Arquivos
**Mudanças:**
- Classes Python agora em pasta `Classes/` (antes na raiz)
- Documentação centralizada em `documentos/`
- Estrutura clara com separação entre domínio e framework

## Navegação Recomendada

### Para Validar Encapsulamento
1. Abra: `Classes/Cliente.py`
2. Procure: `@property` e `@property.setter`
3. Veja: Como atributos privados `_saldo`, `_cpf` são acessados

### Para Validar Classe Abstrata
1. Abra: `Classes/EntidadeBase.py`
2. Procure: `@abstractmethod`
3. Veja: Qualquer classe (ex: `Classes/Produto.py`) implementando `validar()`

### Para Validar Documentação
1. Abra: Qualquer classe em `Classes/`
2. Veja: Docstring no topo da classe
3. Procure: Type hints em cada método

## Verificação de Correções

| Item | Arquivo | Verificar |
|------|---------|-----------|
| **Encapsulamento** | Classes/Produto.py, Classes/Cliente.py, Classes/Pedido.py, Classes/Cozinha.py, Classes/Caixa.py, Classes/Restaurante.py, Classes/Alimento.py, Classes/Comida.py, Classes/Bebida.py, Classes/Combo.py | Presença de `@property` decorators |
| **Classe Abstrata** | Classes/EntidadeBase.py | Método `@abstractmethod validar(self)` |
| **Herança** | Classes/Alimento.py, Classes/Comida.py, Classes/Bebida.py | `class X(Y):` e `super().__init__()` |
| **Documentação** | Classes/ (todas) | Docstrings e type hints |
| **Validações** | Classes/Produto.py, Classes/Cliente.py | Validações em `__init__` e setters |

## Contagem de Linhas

- **Código puro (Python):** ~2,000 linhas
- **Documentação inline:** ~800 linhas (docstrings + type hints)
- **Total Classes/:** ~2,800 linhas

## Recomendações para Validação

1. **Comece por:** `Classes/EntidadeBase.py` (entender o contrato abstrato)
2. **Depois:** `Classes/Produto.py` (entender encapsulamento e herança)
3. **Valide:** Uma classe concreta como `Classes/Cliente.py` ou `Classes/Pedido.py`
4. **Consulte:** `CORRECOES.md` para checklist detalhe

## Próximas Etapas (Sugestões)

- Integração completa com Django apps
- Testes unitários para validações
- API REST completa
- Frontend React funcional

---

**Esclarecimentos:** Para dúvidas específicas sobre implementação, consulte `CORRECOES.md` que lista cada correção com localização exata no código.
