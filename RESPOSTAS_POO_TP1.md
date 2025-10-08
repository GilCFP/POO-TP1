# Respostas do Projeto 1 de POO

## 1 – Tema do Projeto

O tema do Projeto 1 é o desenvolvimento de um sistema para gerenciamento de um restaurante fast-food. O sistema abrange funcionalidades como cadastro de clientes, realização de pedidos, gerenciamento de produtos (alimentos, bebidas, combos), controle de caixa, restrições alimentares, acompanhamento do status dos pedidos, entre outros. O objetivo é simular o funcionamento de um restaurante, desde o atendimento ao cliente até a entrega do pedido, utilizando conceitos fundamentais de Programação Orientada a Objetos (POO).

## 2 – Inserção dos Conceitos de POO

- **Classes:**
  - O projeto é estruturado em torno de classes que representam entidades do domínio, como `Cliente`, `Pedido`, `Produto`, `Alimento`, `Bebida`, `Combo`, `Caixa`, `Restaurante`, `RestricaoAlimentar`, entre outras. Cada classe encapsula atributos e métodos relacionados à sua responsabilidade.

- **Herança:**
  - O conceito de herança é utilizado, por exemplo, nas classes `Alimento` e `Bebida`, que herdam de uma classe base `Produto`. Isso permite o reuso de atributos e métodos comuns, além de especializar comportamentos para cada tipo de produto.

- **Polimorfismo:**
  - O polimorfismo é aplicado ao permitir que métodos como `calcular_preco()` sejam implementados de formas diferentes em subclasses como `Alimento`, `Bebida` e `Combo`, mas possam ser chamados de maneira uniforme a partir de uma referência do tipo `Produto`.

- **Classes Abstratas:**
  - O projeto pode utilizar classes abstratas para definir interfaces comuns, como uma classe abstrata `Produto` que define métodos obrigatórios para suas subclasses, garantindo que todas implementem comportamentos essenciais.

## 3 – Fluxograma Generalista

```
Página Inicial
   |
   v
Login / Cadastro
   |
   v
Menu Principal
   |
   +--> Fazer Pedido
   |      |
   |      v
   |   Escolher Produtos
   |      |
   |      v
   |   Adicionar ao Carrinho
   |      |
   |      v
   |   Finalizar Pedido
   |
   +--> Consultar Status do Pedido
   |
   +--> Gerenciar Cadastro
   |
   +--> Sair
```

*O fluxograma pode ser desenhado em ferramentas como draw.io, Lucidchart ou até mesmo à mão e digitalizado.*

## 4 – Modularização e Organização do Código

As classes principais estão organizadas na pasta `Classes/`, cada uma em seu respectivo arquivo `.py`, facilitando a manutenção e reutilização do código. O projeto utiliza a estrutura de apps do Django, separando funcionalidades em módulos como `cliente`, `pedido`, `produto`, `restaurante` e `core`. Cada app possui subpastas para serviços, templates, arquivos estáticos, etc., promovendo uma arquitetura limpa e escalável.

Exemplo de organização:

```
Classes/
  Alimento.py
  Bebida.py
  Caixa.py
  Cliente.py
  Combo.py
  Comida.py
  Cozinha.py
  Pedido.py
  Produto.py
  Restaurante.py
  RestricaoAlimentar.py
  StatusPedido.py
apps/
  cliente/
  pedido/
  produto/
  restaurante/
  core/
```

*Prints da página do GitHub e explicações podem ser adicionados posteriormente, mostrando a estrutura das pastas e arquivos.*

A modularização foi pensada para separar responsabilidades, facilitar testes e permitir o desenvolvimento paralelo por diferentes membros do grupo.

## 5 – Formatação da Base de Dados

O grupo utiliza o banco de dados SQLite, integrado ao Django. Abaixo, um exemplo de código Python que lê dados da base, realiza uma operação e salva novamente:

```python
import sqlite3

# Conectar ao banco de dados
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Ler dados simplificados (exemplo: clientes)
cursor.execute('SELECT id, nome FROM cliente_cliente')
clientes = cursor.fetchall()
print('Clientes:', clientes)

# Operação: adicionar sufixo ao nome dos clientes
clientes_modificados = [(nome + ' [VIP]', id) for id, nome in clientes]
for nome_mod, id in clientes_modificados:
    cursor.execute('UPDATE cliente_cliente SET nome = ? WHERE id = ?', (nome_mod, id))

conn.commit()

# Verificar alterações
cursor.execute('SELECT id, nome FROM cliente_cliente')
print('Clientes modificados:', cursor.fetchall())

conn.close()
```

*Prints do código, do terminal e do banco de dados antes/depois podem ser adicionados conforme solicitado.*

## 6 – Interface Gráfica

O grupo utiliza a interface web fornecida pelo Django, com templates HTML e integração com frontend (pasta `frontend/`). Não está previsto o uso de interface gráfica desktop.

## 7 – Subdivisão das Implementações

- **Gil:** Classes principais (`Cliente`, `Pedido`, `Produto`), integração com banco de dados, estruturação dos apps Django.
- **Maria:** Implementação dos templates HTML, integração frontend-backend, testes de usabilidade.
- **João:** Serviços e lógica de negócio, implementação de restrições alimentares, documentação e revisão geral.

---

*Observação: Os prints e fluxogramas visuais podem ser adicionados posteriormente conforme a entrega do grupo.*
