import os
import csv
import mercadopago
from datetime import datetime
from twilio.rest import Client
from django.db.models import Q
from django.http import Http404
from django.contrib import messages
from django.contrib.messages.api import success
from django.http import FileResponse, HttpResponse
from vendas.forms import FormPedido, FormPedidoItem
from django.views.generic import ListView, DetailView
from twilio.base.exceptions import TwilioRestException
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from vendas.models import Pedido, PedidoItem, Funcionario
from django.shortcuts import render, redirect, get_object_or_404

class PedidoListView(LoginRequiredMixin, ListView):
    model = Pedido
    paginate_by = 100
    template_name = 'pedido/pedido_list.html'

    def get_queryset(self):
        query = self.request.GET.get('q') or ''
        object_list = self.model.objects.filter(
            Q(id__icontains=query) |
            Q(cliente__nome__icontains=query) |
            Q(cliente__cpf__icontains=query)
        )
        return object_list.order_by('-data_cadastro')

class PedidoDetailView(LoginRequiredMixin, DetailView):
    model = Pedido
    template_name = 'pedido/pedido_detail.html'

def gerar_pagamento(pedido):
    sdk = mercadopago.SDK(os.environ.get('PROD_ACCESS_TOKEN'))
    preference_data = {
        'items': [
            {
                'title': 'DiskFar - Pagamento Online',
                'quantity': 1,
                'unit_price': float(pedido.get_total()),
            }
        ]
    }
    preference_response = sdk.preference().create(preference_data)
    pedido.link_pagamento = preference_response['response']['init_point']
    Pedido.objects.filter(id=pedido.id).update(link_pagamento=pedido.link_pagamento)
    return pedido.link_pagamento

def envia_mensagem_sms(request, pedido, mensagem):
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    client = Client(account_sid, auth_token)
    try:
        client.messages.create(
                                messaging_service_sid=os.environ.get('TWILIO_MESSAGING_SERVICE_SID'),
                                body=f'{mensagem}',
                                to=f'+55{pedido.cliente.celular}'
                            )
        messages.add_message(request, messages.ERROR, f'SMS enviado com sucesso, para o número: {pedido.cliente.celular}', extra_tags='success')
    except TwilioRestException:
        messages.add_message(request, messages.ERROR, f'Não foi possível enviar o SMS, verifique o número cadastrado do cliente: {pedido.cliente.celular}', extra_tags='danger')

def envia_mensagem_whatsapp(request, pedido, mensagem):
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    client = Client(account_sid, auth_token)
    try:
        client.messages.create(
                                from_=os.environ.get('TWILIO_FROM_WHATSAPP'),
                                body=f'{mensagem}',
                                to=f'whatsapp:+55{pedido.cliente.celular}'
                            )
        messages.add_message(request, messages.ERROR, f'WhatsApp enviado com sucesso, para o número: {pedido.cliente.celular}', extra_tags='success')
    except TwilioRestException:
        messages.add_message(request, messages.ERROR, f'Não foi possível enviar o WhatsApp, verifique o número cadastrado do cliente: {pedido.cliente.celular}', extra_tags='danger')

@login_required
def adicionar_pedido(request):
    form_pedido = FormPedido(request.POST or None, request.FILES or None)
    if request.method == 'POST':
        if form_pedido.is_valid():
            new_pedido = form_pedido.save()
            messages.add_message(request, messages.SUCCESS, 'Agora insira os itens do pedido!', extra_tags='success')
            return redirect(f'/pedidos/alterar/{new_pedido.id}')
        else:
            messages.add_message(request, messages.ERROR, 'Erro no formulário, tente novamente!', extra_tags='danger')       
    return render(request, 'pedido/pedido_add.html', {'form_pedido': form_pedido})

@login_required
def remover_pedido(request, id):
    if request.method == 'GET':
        pedido = Pedido.objects.get(id=id)
        itens = PedidoItem.objects.filter(pedido=id)
        for item in itens:
            item.produto.quantidade += item.quantidade
            item.produto.save()
        comprovante = Pedido.objects.get(id=pedido.id).comprovante.name
        if comprovante:
            pedido.comprovante.storage.delete(pedido.comprovante.name)
        pedido.delete()
        return redirect('/pedidos')
    else:
        return render(request, 'pedido/pedido_list.html')

@login_required
def alterar_pedido(request, id):
    instance = get_object_or_404(Pedido, id=id)
    pedido = Pedido.objects.get(id=id)
    itens = PedidoItem.objects.filter(pedido=id)
    total_itens = pedido.get_total_itens()
    form_pedido = FormPedido(request.POST or None, request.FILES or None, instance=instance)
    form_item = FormPedidoItem(request.POST or None)
    if request.method == 'POST':
        if form_pedido.is_valid():
            old_comprovante = Pedido.objects.get(id=pedido.id).comprovante.name
            if not old_comprovante:
                form_pedido.save()
            elif form_pedido.cleaned_data['comprovante'] != old_comprovante:
                pedido.comprovante.storage.delete(pedido.comprovante.name)
            form_pedido.save()
            pedido = Pedido.objects.get(id=id)
            gerar_pagamento(pedido)
            messages.add_message(request, messages.SUCCESS, 'Pedido alterado!', extra_tags='success')
            if form_pedido.cleaned_data['status'] == 'R':
                mensagem = f'Olá {pedido.cliente.nome}, tudo bem? ☺️\n\nStatus do pedido: *{pedido.get_status_display()}*!\n\nValor total: {pedido.get_total():.2f}\n\nObrigado por comprar conosco!\n\nCaso deseje realizar o pagamento online, segue link: {pedido.link_pagamento}\n\n*Observação*: Encaminhar o comprovante de pagamento para evitar cobrança no local de entrega!\n\nAtenciosamente,\nDiskFar - Drogaria e Farmácia 💙'
                envia_mensagem_whatsapp(request, Pedido.objects.get(id=id), mensagem)
                envia_mensagem_sms(request, Pedido.objects.get(id=id), mensagem.replace('*', ''))
            elif form_pedido.cleaned_data['status'] == 'A':
                mensagem = f'Olá {pedido.cliente.nome},\n\nStatus do pedido: *{pedido.get_status_display()}* 🏍️\n\nSeu pedido está a caminho, obrigado pela preferência.\n\nAtenciosamente,\nDiskFar - Drogaria e Farmácia 💙'
                envia_mensagem_whatsapp(request, Pedido.objects.get(id=id), mensagem)
                envia_mensagem_sms(request, Pedido.objects.get(id=id), mensagem.replace('*', ''))
            elif form_pedido.cleaned_data['status'] == 'E':
                mensagem = f'Olá {pedido.cliente.nome},\n\nStatus do pedido: *{pedido.get_status_display()}* 🎉\n\nSeu pedido foi entregue, obrigado pela preferência.\n\nQualquer dúvida ou reclamação, estamos à disposição 😊\n\nAtenciosamente,\nDiskFar - Drogaria e Farmácia 💙'
                envia_mensagem_whatsapp(request, Pedido.objects.get(id=id), mensagem)
                envia_mensagem_sms(request, Pedido.objects.get(id=id), mensagem.replace('*', ''))
            return redirect(f'/pedidos/alterar/{pedido.id}')
        else:
            messages.add_message(request, messages.ERROR, 'Erro no formulário, tente novamente!', extra_tags='danger')
            return render(request, 'pedido/pedido_edit.html', {'form': form_pedido})
    else:
        return render(request, 'pedido/pedido_edit.html', {'form_pedido': form_pedido, 'form_item' : form_item, 'pedido': pedido, 'itens': itens, 'total_itens': total_itens})

@login_required
def alterar_item(request, id_pedido):
    pedido = Pedido.objects.get(id=id_pedido)
    form_item = FormPedidoItem(request.POST or None)
    if request.method == 'POST':
        if form_item.is_valid():
            new_item = PedidoItem(
                pedido=pedido,
                produto=form_item.cleaned_data['produto'],
                quantidade=form_item.cleaned_data['quantidade']
            )
            if new_item.quantidade > new_item.produto.quantidade:
                messages.add_message(request, messages.ERROR, 'Quantidade de produtos informada maior que a disponível!', extra_tags='danger')
            else:
                new_item.produto.quantidade -= new_item.quantidade
                new_item.produto.save()
               
                item = PedidoItem.objects.filter(pedido=pedido, produto=new_item.produto)
                if item:
                    item[0].quantidade += new_item.quantidade
                    item[0].save()
                else:
                    new_item.produto.save()
                    new_item.save()
            messages.add_message(request, messages.SUCCESS, 'Item adicionado!', extra_tags='success')
            gerar_pagamento(pedido)
    return redirect(f'/pedidos/alterar/{id_pedido}')

@login_required
def remover_item(request, id_pedido, id_item):
    if request.method == 'GET':
        try:
            item = PedidoItem.objects.get(id=id_item)
            messages.add_message(request, messages.SUCCESS, 'Item removido!', extra_tags='success')
        except:
            messages.add_message(request, messages.ERROR, 'Não foi possível remover item do pedido!', extra_tags='danger')
            return redirect('/pedidos')                                    
        item.produto.quantidade += item.quantidade
        item.produto.save()
        item.delete()
        return redirect(f'/pedidos/alterar/{id_pedido}')

@login_required
def adicionar_filtro(request):
    if request.user.has_perm('vendas.view_pedido'):
        data_inicial = datetime.strptime(request.POST.get('data_inicio'), '%Y-%m-%d')
        data_final = datetime.strptime(request.POST.get('data_final') + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
        if request.method == 'POST':
            pedidos = Pedido.objects.filter(data_cadastro__gte=data_inicial, data_cadastro__lte=data_final)
            if pedidos:
                response = HttpResponse(                
                    content_type='text/csv',
                    headers={'Content-Disposition': f'attachment; filename="relatorio_pedidos_{datetime.now().strftime("%d/%m/%Y")}.csv"'},
                )
                writer = csv.writer(response, delimiter=';')
                writer.writerow(['Pedido', 'Data de Cadastro', 'Funcionario', 'Valor Total'])
                for pedido in pedidos:
                    writer.writerow([pedido.id, pedido.data_cadastro.strftime('%d/%m/%Y'), pedido.funcionario.nome, f'{pedido.get_total():.2f}'])
                    messages.add_message(request, messages.SUCCESS, 'Relátorio gerado com sucesso!', extra_tags='success')
                return response
            else:
                messages.add_message(request, messages.ERROR, 'Nenhum pedido encontrado neste período!', extra_tags='danger')
        return redirect('/pedidos')
    return redirect('/')
