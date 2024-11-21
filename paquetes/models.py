from django.db import models

class Estado(models.Model):
	nombre = models.CharField(max_length=100, unique=True)
	latitud = models.FloatField()
	region = models.CharField(max_length=50)

	def __str__(self):
		return self.nombre


class Frase(models.Model):
	frase = models.CharField(max_length=255)

	def __str__(self):
		return self.frase


class Paquete(models.Model):
	codigo = models.CharField(max_length=100, unique=True)  # Código único del paquete
	descripcion = models.TextField()  # Descripción del paquete
	peso = models.FloatField()  # Peso del paquete en kilogramos
	estado_actual = models.ForeignKey(
		Estado, on_delete=models.SET_NULL, null=True, related_name='paquetes'
	)  # Estado actual donde se encuentra el paquete
	fecha_envio = models.DateTimeField(auto_now_add=True)  # Fecha de envío del paquete
	fecha_entrega = models.DateTimeField(null=True, blank=True)  # Fecha de entrega estimada o real
	estado_paquete = models.CharField(
		max_length=50,
		choices=[
			('En tránsito', 'En tránsito'),
			('Recolección', 'Recolección'),
			('Entregado', 'Entregado'),
		],
		default='En tránsito',
	)

	def __str__(self):
		return f"Paquete {self.codigo} - {self.estado_paquete}"


class Ruta(models.Model):
	paquete = models.ForeignKey(
		Paquete, on_delete=models.CASCADE, related_name='rutas'
	)  # Relación con el paquete
	frase = models.ForeignKey(
		Frase, on_delete=models.CASCADE, related_name='rutas'
	)  # Relación con la frase utilizada para describir el estado
	estado_origen = models.ForeignKey(
		Estado, on_delete=models.CASCADE, related_name='rutas_origen'
	)  # Estado de origen del paquete
	estado_destino = models.ForeignKey(
		Estado, on_delete=models.CASCADE, related_name='rutas_destino'
	)  # Estado de destino del paquete
	fecha_actualizacion = models.DateTimeField(auto_now_add=True)  # Fecha de actualización de la ruta

	def __str__(self):
		return f"Ruta de {self.estado_origen} a {self.estado_destino} - Paquete {self.paquete.codigo}"
