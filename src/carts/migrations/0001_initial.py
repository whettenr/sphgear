# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-19 05:09
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('products', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_item', models.PositiveIntegerField(blank=True, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('subtotal', models.DecimalField(decimal_places=2, default=25.0, max_digits=50)),
                ('tax_percentage', models.DecimalField(decimal_places=5, default=0.085, max_digits=10)),
                ('tax_total', models.DecimalField(decimal_places=2, default=25.0, max_digits=50)),
                ('total', models.DecimalField(decimal_places=2, default=25.0, max_digits=50)),
            ],
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('line_item_total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='carts.Cart')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.Variation')),
            ],
        ),
        migrations.AddField(
            model_name='cart',
            name='items',
            field=models.ManyToManyField(through='carts.CartItem', to='products.Variation'),
        ),
        migrations.AddField(
            model_name='cart',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
