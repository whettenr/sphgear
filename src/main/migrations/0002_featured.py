# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-22 01:14
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import main.models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_auto_20170122_0114'),
        ('posts', '0001_initial'),
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Featured',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=120, unique=True)),
                ('text', models.CharField(blank=True, max_length=220, null=True)),
                ('button_animation', models.CharField(blank=True, choices=[('Fade in', (('fadeIn', 'Fade In'), ('fadeInLeft', 'Fade in Left'), ('fadeInRight', 'Fade in Right'), ('fadeInUp', 'Fade in Up'), ('fadeInDown', 'Fade in Down'))), ('Flip in', (('flip', 'flip'), ('flipInX', 'Flip in X'), ('flipInY', 'Flip in Y'))), ('Zoom in', (('zoomInUp', 'Zoom In Up'), ('zoomInDown', 'Zoom In Down'), ('zoomInLeft', 'Zoom in Left'), ('zoomInRight', 'Zoom in Right'))), ('lightSpeedIn', 'Light Speed In')], max_length=20, null=True)),
                ('title_animation', models.CharField(choices=[('Fade in', (('fadeIn', 'Fade In'), ('fadeInLeft', 'Fade in Left'), ('fadeInRight', 'Fade in Right'), ('fadeInUp', 'Fade in Up'), ('fadeInDown', 'Fade in Down'))), ('Flip in', (('flip', 'flip'), ('flipInX', 'Flip in X'), ('flipInY', 'Flip in Y'))), ('Zoom in', (('zoomInUp', 'Zoom In Up'), ('zoomInDown', 'Zoom In Down'), ('zoomInLeft', 'Zoom in Left'), ('zoomInRight', 'Zoom in Right'))), ('lightSpeedIn', 'Light Speed In')], max_length=20)),
                ('text_animation', models.CharField(choices=[('Fade in', (('fadeIn', 'Fade In'), ('fadeInLeft', 'Fade in Left'), ('fadeInRight', 'Fade in Right'), ('fadeInUp', 'Fade in Up'), ('fadeInDown', 'Fade in Down'))), ('Flip in', (('flip', 'flip'), ('flipInX', 'Flip in X'), ('flipInY', 'Flip in Y'))), ('Zoom in', (('zoomInUp', 'Zoom In Up'), ('zoomInDown', 'Zoom In Down'), ('zoomInLeft', 'Zoom in Left'), ('zoomInRight', 'Zoom in Right'))), ('lightSpeedIn', 'Light Speed In')], max_length=10)),
                ('image', models.ImageField(upload_to=main.models.image_upload_to_featured)),
                ('position', models.CharField(choices=[('slide_style_center', 'Center'), ('slide_style_left', 'Left'), ('slide_style_right', 'Right')], default='left', max_length=20)),
                ('active', models.BooleanField(default=True)),
                ('post', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='posts.Post')),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='products.Product')),
            ],
        ),
    ]