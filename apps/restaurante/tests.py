from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
import json

from .models import Restaurante, Cozinha, Caixa
from apps.cliente.models import Cliente
from apps.pedido.models import Pedido, ItemPedido, StatusPedido
from apps.produto.models import Produto
from apps.pedido.services.pedido_service import PedidoService


class KanbanSystemTestCase(TestCase):
    """Testes completos para o sistema kanban do restaurante."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        # Criar usuário para autenticação
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Criar cliente de teste (usando CPF válido)
        self.client_obj = Cliente.objects.create(
            cpf='11144477735',  # CPF válido para testes
            name='João Silva',
            email='joao@test.com',
            phone='11999999999',
            balance=Decimal('100.00')
        )
        
        # Criar produtos de teste
        self.produto1 = Produto.objects.create(
            name='Hambúrguer Clássico',
            price=Decimal('25.90'),
            available=True
        )
        
        self.produto2 = Produto.objects.create(
            name='Batata Frita',
            price=Decimal('12.50'),
            available=True
        )
        
        # Criar restaurante
        self.restaurante = Restaurante.objects.create(
            name='Fast Food Test',
            description='Restaurante de teste',
            address='Rua Teste, 123',
            phone='11999999999',
            email='test@restaurant.com',
            opening_time='08:00',
            closing_time='22:00'
        )
        
        # Criar cozinha
        self.cozinha = Cozinha.objects.create(
            restaurante=self.restaurante,
            number_of_chefs=2,
            number_of_stations=3,
            is_active=True
        )
        
        # Criar caixa
        self.caixa = Caixa.objects.create(
            restaurante=self.restaurante
        )
        
        # Cliente HTTP para testes
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
    
    def test_kanban_view_loads_correctly(self):
        """Testa se a view principal do kanban carrega corretamente."""
        url = reverse('restaurante:kanban')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'orders_by_status')
        self.assertContains(response, 'status_choices')
        self.assertContains(response, 'cozinha_info')
    
    def test_kanban_api_returns_correct_data(self):
        """Testa se a API do kanban retorna dados corretos."""
        # Criar pedidos em diferentes status
        pedido1 = self._create_test_order(StatusPedido.WAITING)
        pedido2 = self._create_test_order(StatusPedido.PREPARING)
        pedido3 = self._create_test_order(StatusPedido.READY)
        
        # Adicionar pedidos aos relacionamentos da cozinha
        self.cozinha.orders_in_queue.add(pedido1)
        self.cozinha.orders_in_progress.add(pedido2)
        self.cozinha.orders_ready.add(pedido3)
        
        url = reverse('restaurante_api:kanban_api')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertTrue(data['success'])
        self.assertIn('orders_by_status', data)
        self.assertIn('status_choices', data)
        self.assertIn('cozinha_info', data)
        
        # Verificar se os pedidos estão nos status corretos
        orders_by_status = data['orders_by_status']
        self.assertEqual(len(orders_by_status[StatusPedido.WAITING]['orders']), 1)
        self.assertEqual(len(orders_by_status[StatusPedido.PREPARING]['orders']), 1)
        self.assertEqual(len(orders_by_status[StatusPedido.READY]['orders']), 1)
    
    def test_status_update_workflow(self):
        """Testa o workflow completo de atualização de status."""
        # Criar pedido inicial
        pedido = self._create_test_order(StatusPedido.WAITING)
        self.cozinha.orders_in_queue.add(pedido)
        
        # Testar avanço de WAITING para PREPARING
        url = reverse('restaurante_api:kanban_advance_status', args=[pedido.id])
        response = self.client.post(url, content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        
        # Verificar se o pedido mudou de status
        pedido.refresh_from_db()
        self.assertEqual(pedido.status, StatusPedido.PREPARING)
        
        # Testar avanço de PREPARING para READY
        response = self.client.post(url, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        pedido.refresh_from_db()
        self.assertEqual(pedido.status, StatusPedido.READY)
        
        # Testar avanço de READY para BEING_DELIVERED
        response = self.client.post(url, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        pedido.refresh_from_db()
        self.assertEqual(pedido.status, StatusPedido.BEING_DELIVERED)
    
    def test_manual_status_change(self):
        """Testa mudança manual de status."""
        pedido = self._create_test_order(StatusPedido.WAITING)
        
        # Testar mudança manual para PREPARING
        url = reverse('restaurante_api:kanban_status_update', args=[pedido.id])
        data = {'status': StatusPedido.PREPARING}
        response = self.client.post(
            url, 
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertTrue(response_data['success'])
        
        pedido.refresh_from_db()
        self.assertEqual(pedido.status, StatusPedido.PREPARING)
    
    def test_invalid_status_transitions(self):
        """Testa validações de transições de status inválidas."""
        pedido = self._create_test_order(StatusPedido.DELIVERED)
        
        # Tentar avançar pedido já entregue
        url = reverse('restaurante_api:kanban_advance_status', args=[pedido.id])
        response = self.client.post(url, content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('já foi entregue', data['error'])
    
    def test_kitchen_relationships_update(self):
        """Testa se os relacionamentos da cozinha são atualizados corretamente."""
        pedido = self._create_test_order(StatusPedido.WAITING)
        self.cozinha.orders_in_queue.add(pedido)
        
        # Verificar estado inicial
        self.assertEqual(self.cozinha.orders_in_queue.count(), 1)
        self.assertEqual(self.cozinha.orders_in_progress.count(), 0)
        
        # Avançar para PREPARING
        url = reverse('restaurante_api:kanban_advance_status', args=[pedido.id])
        response = self.client.post(url, content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        # Verificar se os relacionamentos foram atualizados
        self.assertEqual(self.cozinha.orders_in_queue.count(), 0)
        self.assertEqual(self.cozinha.orders_in_progress.count(), 1)
        
        # Avançar para READY
        response = self.client.post(url, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        # Verificar relacionamentos
        self.assertEqual(self.cozinha.orders_in_progress.count(), 0)
        self.assertEqual(self.cozinha.orders_ready.count(), 1)
        
        # Avançar para BEING_DELIVERED
        response = self.client.post(url, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        # Verificar que foi removido de todos os relacionamentos
        self.assertEqual(self.cozinha.orders_ready.count(), 0)
    
    def test_order_data_format(self):
        """Testa se os dados dos pedidos estão no formato correto."""
        pedido = self._create_test_order(StatusPedido.WAITING)
        self.cozinha.orders_in_queue.add(pedido)
        
        url = reverse('restaurante_api:kanban_api')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        orders = data['orders_by_status'][StatusPedido.WAITING]['orders']
        self.assertEqual(len(orders), 1)
        
        order_data = orders[0]
        
        # Verificar estrutura dos dados
        self.assertIn('id', order_data)
        self.assertIn('cliente', order_data)
        self.assertIn('total', order_data)
        self.assertIn('criado_em', order_data)
        self.assertIn('items', order_data)
        
        # Verificar dados do cliente
        self.assertEqual(order_data['cliente']['nome'], self.client_obj.name)
        
        # Verificar itens
        self.assertEqual(len(order_data['items']), 2)  # 2 produtos adicionados
    
    def test_error_handling(self):
        """Testa tratamento de erros."""
        # Testar pedido inexistente
        url = reverse('restaurante_api:kanban_status_update', args=[99999])
        data = {'status': StatusPedido.PREPARING}
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertFalse(response_data['success'])
        self.assertIn('não encontrado', response_data['error'])
        
        # Testar status inválido
        pedido = self._create_test_order(StatusPedido.WAITING)
        url = reverse('restaurante_api:kanban_status_update', args=[pedido.id])
        data = {'status': 'INVALID_STATUS'}
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertFalse(response_data['success'])
        self.assertIn('inválido', response_data['error'])
    
    def test_url_routing(self):
        """Testa se o roteamento de URLs está funcionando corretamente."""
        # Testar URL da view principal
        url = reverse('restaurante:kanban')
        self.assertEqual(url, '/restaurante/kanban/')
        
        # Testar URLs da API
        api_url = reverse('restaurante_api:kanban_api')
        self.assertEqual(api_url, '/api/restaurante/kanban/orders/')
        
        status_url = reverse('restaurante_api:kanban_status_update', args=[1])
        self.assertEqual(status_url, '/api/restaurante/kanban/orders/1/status/')
        
        advance_url = reverse('restaurante_api:kanban_advance_status', args=[1])
        self.assertEqual(advance_url, '/api/restaurante/kanban/orders/1/advance/')
    
    def test_complete_workflow_integration(self):
        """Testa o workflow completo de ponta a ponta."""
        # 1. Criar pedido
        pedido = PedidoService.criar_pedido(
            cliente_id=self.client_obj.id,
            delivery_address='Rua Teste, 456',
            notes='Sem cebola'
        )
        
        # 2. Adicionar itens
        PedidoService.adicionar_item(pedido.id, self.produto1.id, 2)
        PedidoService.adicionar_item(pedido.id, self.produto2.id, 1)
        
        # 3. Finalizar pedido
        pedido = PedidoService.finalizar_pedido(pedido.id)
        
        # 4. Processar pagamento
        pedido = PedidoService.processar_pagamento(pedido.id)
        
        # 5. Adicionar à cozinha
        self.cozinha.orders_in_queue.add(pedido)
        
        # 6. Verificar se aparece no kanban
        url = reverse('restaurante_api:kanban_api')
        response = self.client.get(url)
        data = response.json()
        
        waiting_orders = data['orders_by_status'][StatusPedido.WAITING]['orders']
        self.assertEqual(len(waiting_orders), 1)
        self.assertEqual(waiting_orders[0]['id'], pedido.id)
        
        # 7. Avançar através dos status
        advance_url = reverse('restaurante_api:kanban_advance_status', args=[pedido.id])
        
        # WAITING -> PREPARING
        response = self.client.post(advance_url, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        # PREPARING -> READY
        response = self.client.post(advance_url, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        # READY -> BEING_DELIVERED
        response = self.client.post(advance_url, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        # 8. Verificar estado final
        pedido.refresh_from_db()
        self.assertEqual(pedido.status, StatusPedido.BEING_DELIVERED)
        
        # 9. Verificar que não está mais em nenhum relacionamento da cozinha
        self.assertEqual(self.cozinha.orders_in_queue.count(), 0)
        self.assertEqual(self.cozinha.orders_in_progress.count(), 0)
        self.assertEqual(self.cozinha.orders_ready.count(), 0)
    
    def _create_test_order(self, status=StatusPedido.ORDERING):
        """Método auxiliar para criar pedidos de teste."""
        pedido = Pedido.objects.create(
            cliente=self.client_obj,
            status=status,
            delivery_address='Rua Teste, 123',
            notes='Pedido de teste'
        )
        
        # Adicionar itens
        ItemPedido.objects.create(
            pedido=pedido,
            produto=self.produto1,
            quantidade=1,
            unit_price=self.produto1.price
        )
        
        ItemPedido.objects.create(
            pedido=pedido,
            produto=self.produto2,
            quantidade=2,
            unit_price=self.produto2.price
        )
        
        # Calcular total
        pedido.calculate_total()
        
        return pedido


class KanbanViewsTestCase(TestCase):
    """Testes específicos para as views do kanban."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
    
    def test_kanban_view_without_kitchen(self):
        """Testa a view do kanban quando não há cozinha configurada."""
        url = reverse('restaurante:kanban')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'orders_by_status')
        
        # Verificar se os dados estão vazios
        context = response.context
        self.assertEqual(context['orders_by_status'], {})
        self.assertIsNone(context['cozinha_info'])
    
    def test_authentication_required(self):
        """Testa se a autenticação é obrigatória."""
        self.client.logout()
        
        # Testar view principal
        url = reverse('restaurante:kanban')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirect para login
        
        # Testar API
        api_url = reverse('restaurante_api:kanban_api')
        response = self.client.get(api_url)
        self.assertEqual(response.status_code, 302)  # Redirect para login
