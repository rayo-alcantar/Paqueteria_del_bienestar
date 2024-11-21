from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Paquete, Estado, Ruta, Frase
from .serializers import PaqueteSerializer, RutaSerializer
import uuid

class CrearPaqueteView(APIView):
	"""
	Vista para crear un paquete, generar su ruta y asignar el número de rastreo.
	"""
	def post(self, request, *args, **kwargs):
		# Serializar los datos de entrada
		serializer = PaqueteSerializer(data=request.data)
		if serializer.is_valid():
			# Generar el código único para el paquete
			codigo = str(uuid.uuid4()).replace("-", "").upper()[:10]  # Código robusto
			paquete = serializer.save(codigo=codigo)  # Guardar el paquete con el código generado
			
			# Obtener estados de origen y destino
			estado_origen = Estado.objects.get(pk=request.data["estado_origen_id"])
			estado_destino = Estado.objects.get(pk=request.data["estado_destino_id"])
			
			# Generar la ruta automáticamente con frases
			frases = Frase.objects.all()
			Ruta.objects.create(
				paquete=paquete,
				frase=frases[0],  # Frase inicial
				estado_origen=estado_origen,
				estado_destino=estado_destino,
			)

			# Simular pasos intermedios (opcional, según tu lógica de negocio)
			if estado_origen.region != estado_destino.region:
				estados_intermedios = Estado.objects.filter(
					region__in=["Centro", "Norte", "Sur"]
				).exclude(pk__in=[estado_origen.pk, estado_destino.pk])[:3]
				for estado in estados_intermedios:
					Ruta.objects.create(
						paquete=paquete,
						frase=frases[1],  # Frase intermedia
						estado_origen=estado_origen,
						estado_destino=estado,
					)

			# Ruta final
			Ruta.objects.create(
				paquete=paquete,
				frase=frases[2],  # Frase final
				estado_origen=estado_origen,
				estado_destino=estado_destino,
			)

			return Response({"codigo": codigo}, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DetallePaqueteView(generics.RetrieveAPIView):
	"""
	Vista para obtener los detalles de un paquete por su código.
	"""
	queryset = Paquete.objects.all()
	serializer_class = PaqueteSerializer
	lookup_field = "codigo"  # Permite buscar el paquete por su código


class ListarPaquetesView(generics.ListAPIView):
	"""
	Vista para listar todos los paquetes con opción a filtrar por estado.
	"""
	queryset = Paquete.objects.all()
	serializer_class = PaqueteSerializer

	def get_queryset(self):
		# Permitir filtrar por el estado actual del paquete
		estado = self.request.query_params.get("estado_actual")
		if estado:
			return Paquete.objects.filter(estado_actual__nombre=estado)
		return super().get_queryset()


class RutasPaqueteView(generics.ListAPIView):
	"""
	Vista para listar las rutas de un paquete específico.
	"""
	serializer_class = RutaSerializer

	def get_queryset(self):
		# Obtener el paquete por su código
		paquete_codigo = self.kwargs.get("codigo")
		return Ruta.objects.filter(paquete__codigo=paquete_codigo)


