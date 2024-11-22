# Generated by Django 3.1.12 on 2024-11-22 21:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Estado',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, unique=True)),
                ('latitud', models.FloatField(blank=True, default=0.0, null=True)),
                ('longitud', models.FloatField(blank=True, default=0.0, null=True)),
                ('region', models.CharField(blank=True, max_length=50, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Frase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('frase', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Paquete',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(blank=True, max_length=100, unique=True)),
                ('remitente', models.CharField(max_length=255)),
                ('direccion_recoleccion', models.TextField()),
                ('receptor', models.CharField(max_length=255)),
                ('direccion_entrega', models.TextField()),
                ('descripcion', models.TextField()),
                ('peso', models.FloatField()),
                ('fecha_envio', models.DateTimeField(auto_now_add=True)),
                ('fecha_entrega', models.DateTimeField(blank=True, null=True)),
                ('estado_paquete', models.CharField(choices=[('En tránsito', 'En tránsito'), ('Recolección', 'Recolección'), ('Entregado', 'Entregado'), ('Retrasado', 'Retrasado'), ('Cancelado', 'Cancelado')], default='En tránsito', max_length=50)),
                ('estado_actual', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='paquetes', to='paquetes.estado')),
            ],
        ),
        migrations.CreateModel(
            name='Ruta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_actualizacion', models.DateTimeField(auto_now_add=True)),
                ('estado_destino', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rutas_destino', to='paquetes.estado')),
                ('estado_origen', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rutas_origen', to='paquetes.estado')),
                ('frase', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rutas', to='paquetes.frase')),
                ('paquete', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rutas', to='paquetes.paquete')),
            ],
        ),
    ]
