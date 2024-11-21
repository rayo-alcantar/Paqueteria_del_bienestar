from rest_framework import serializers
from .models import Estado, Frase, Paquete, Ruta

class PaqueteSerializer(serializers.ModelSerializer):
	estado_origen_id = serializers.PrimaryKeyRelatedField(
		queryset=Estado.objects.all(), source="rutas.first.estado_origen", write_only=True
	)
	estado_destino_id = serializers.PrimaryKeyRelatedField(
		queryset=Estado.objects.all(), source="rutas.first.estado_destino", write_only=True
	)

	class Meta:
		model = Paquete
		fields = [
			"codigo",  # Ahora el código será solo lectura
			"descripcion",
			"peso",
			"estado_actual",
			"fecha_envio",
			"fecha_entrega",
			"estado_paquete",
			"estado_origen_id",
			"estado_destino_id",
		]
		read_only_fields = ["codigo", "estado_actual", "fecha_envio", "estado_paquete"]

class EstadoSerializer(serializers.ModelSerializer):
	class Meta:
		model = Estado
		fields = ['id', 'nombre', 'latitud', 'region']  # Incluimos los campos importantes

class FraseSerializer(serializers.ModelSerializer):
	class Meta:
		model = Frase
		fields = ['id', 'frase']

class RutaSerializer(serializers.ModelSerializer):
	paquete = PaqueteSerializer(read_only=True)  # Mostrar información del paquete
	paquete_id = serializers.PrimaryKeyRelatedField(
		queryset=Paquete.objects.all(), source='paquete', write_only=True
	)  # Para asignar el paquete por ID
	frase = FraseSerializer(read_only=True)
	frase_id = serializers.PrimaryKeyRelatedField(
		queryset=Frase.objects.all(), source='frase', write_only=True
	)
	estado_origen = EstadoSerializer(read_only=True)
	estado_origen_id = serializers.PrimaryKeyRelatedField(
		queryset=Estado.objects.all(), source='estado_origen', write_only=True
	)
	estado_destino = EstadoSerializer(read_only=True)
	estado_destino_id = serializers.PrimaryKeyRelatedField(
		queryset=Estado.objects.all(), source='estado_destino', write_only=True
	)

	class Meta:
		model = Ruta
		fields = [
			'id', 'paquete', 'paquete_id', 'frase', 'frase_id', 
			'estado_origen', 'estado_origen_id', 'estado_destino', 
			'estado_destino_id', 'fecha_actualizacion'
		]
