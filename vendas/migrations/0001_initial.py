# Generated by Django 3.2.6 on 2022-03-14 23:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('produtos', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cargo',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nome', models.CharField(max_length=30, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Clientes',
            fields=[
                ('email', models.CharField(max_length=80)),
                ('telefone', models.CharField(blank=True, max_length=10, null=True)),
                ('celular', models.CharField(blank=True, max_length=11, null=True)),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nome', models.CharField(max_length=30)),
                ('cpf', models.CharField(blank=True, max_length=11, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Funcionario',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nome', models.CharField(max_length=30)),
                ('cpf', models.CharField(max_length=11)),
                ('data_nascimento', models.DateField()),
                ('cargo', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='vendas.cargo')),
                ('usuario', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Pedido',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('data_cadastro', models.DateTimeField(auto_now_add=True)),
                ('cep', models.CharField(blank=True, max_length=9)),
                ('endereco', models.CharField(blank=True, max_length=300)),
                ('bairro', models.CharField(blank=True, max_length=100)),
                ('numero', models.CharField(blank=True, max_length=10)),
                ('comprovante', models.ImageField(blank=True, null=True, upload_to='images/comprovantes')),
                ('taxa_entrega', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=5, null=True)),
                ('status', models.CharField(choices=[('R', 'Realizado'), ('P', 'Em preparação'), ('A', 'A caminho'), ('E', 'Entregue'), ('C', 'Cancelado')], max_length=10)),
                ('link_pagamento', models.TextField(blank=True, null=True)),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pedido_cliente', to='vendas.clientes')),
                ('funcionario', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='vendas.funcionario')),
            ],
        ),
        migrations.CreateModel(
            name='PedidoItem',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('quantidade', models.IntegerField()),
                ('pedido', models.ForeignKey(blank=None, null=None, on_delete=django.db.models.deletion.CASCADE, to='vendas.pedido')),
                ('produto', models.ForeignKey(blank=None, null=None, on_delete=django.db.models.deletion.DO_NOTHING, to='produtos.produto')),
            ],
        ),
    ]
