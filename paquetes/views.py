from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Paquete, Estado, Ruta, Frase
from .serializers import PaqueteSerializer, RutaSerializer
import uuid

# Vista para la página principal
def index(request):
	return render(request, 'paquetes/index.html')

# Vista para rastrear paquete
def rastrear_paquete(request):
	if request.method == "POST":
		codigo = request.POST.get("codigo")
		try:
			paquete = Paquete.objects.get(codigo=codigo)
			rutas = Ruta.objects.filter(paquete=paquete)
			return render(request, 'paquetes/rastreo_paquete.html', {"paquete": paquete, "rutas": rutas})
		except Paquete.DoesNotExist:
			error = "El número de rastreo ingresado no existe."
			return render(request, 'paquetes/rastreo_paquete.html', {"error": error})
	return render(request, 'paquetes/rastreo_paquete.html')

# Vista para solicitar envío
def solicitar_envio(request):
	if request.method == "POST":
		descripcion = request.POST.get("descripcion")
		peso = request.POST.get("peso")
		estado_origen_id = request.POST.get("estado_origen")
		estado_destino_id = request.POST.get("estado_destino")
		
		try:
			# Crear el paquete
			estado_origen = Estado.objects.get(pk=estado_origen_id)
			estado_destino = Estado.objects.get(pk=estado_destino_id)
			codigo = str(uuid.uuid4()).replace("-", "").upper()[:10]  # Código robusto
			paquete = Paquete.objects.create(
				codigo=codigo,
				descripcion=descripcion,
				peso=peso,
				estado_actual=estado_origen,
			)

			# Generar rutas automáticamente
			frases = Frase.objects.all()
			Ruta.objects.create(
				paquete=paquete,
				frase=frases[0],
				estado_origen=estado_origen,
				estado_destino=estado_destino,
			)
			if estado_origen.region != estado_destino.region:
				estados_intermedios = Estado.objects.filter(
					region__in=["Centro", "Norte", "Sur"]
				).exclude(pk__in=[estado_origen.pk, estado_destino.pk])[:3]
				for estado in estados_intermedios:
					Ruta.objects.create(
						paquete=paquete,
						frase=frases[1],
						estado_origen=estado_origen,
						estado_destino=estado,
					)
			Ruta.objects.create(
				paquete=paquete,
				frase=frases[2],
				estado_origen=estado_origen,
				estado_destino=estado_destino,
			)

			# Devolver el número de rastreo
			return render(request, 'paquetes/solicitar_envio.html', {"codigo": codigo, "success": True})
		except Exception as e:
			error = f"Hubo un error al procesar tu solicitud: {e}"
			return render(request, 'paquetes/solicitar_envio.html', {"error": error})

	return render(request, 'paquetes/solicitar_envio.html')

# Vista "Acerca de"
def acerca_de(request):
	return render(request, 'paquetes/acerca_de.html')

# API Views

class CrearPaqueteView(APIView):
	"""
	Vista para crear un paquete, generar su ruta y asignar el número de rastreo.
	"""
	def post(self, request, *args, **kwargs):
		serializer = PaqueteSerializer(data=request.data)
		if serializer.is_valid():
			codigo = str(uuid.uuid4()).replace("-", "").upper()[:10]
			paquete = serializer.save(codigo=codigo)
			estado_origen = Estado.objects.get(pk=request.data["estado_origen_id"])
			estado_destino = Estado.objects.get(pk=request.data["estado_destino_id"])
			frases = Frase.objects.all()
			Ruta.objects.create(
				paquete=paquete,
				frase=frases[0],
				estado_origen=estado_origen,
				estado_destino=estado_destino,
			)
			if estado_origen.region != estado_destino.region:
				estados_intermedios = Estado.objects.filter(
					region__in=["Centro", "Norte", "Sur"]
				).exclude(pk__in=[estado_origen.pk, estado_destino.pk])[:3]
				for estado in estados_intermedios:
					Ruta.objects.create(
						paquete=paquete,
						frase=frases[1],
						estado_origen=estado_origen,
						estado_destino=estado,
					)
			Ruta.objects.create(
				paquete=paquete,
				frase=frases[2],
				estado_origen=estado_origen,
				estado_destino=estado_destino,
			)
			return Response({"codigo": codigo}, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DetallePaqueteView(generics.RetrieveAPIView):
	queryset = Paquete.objects.all()
	serializer_class = PaqueteSerializer
	lookup_field = "codigo"

class ListarPaquetesView(generics.ListAPIView):
	queryset = Paquete.objects.all()
	serializer_class = PaqueteSerializer

	def get_queryset(self):
		estado = self.request.query_params.get("estado_actual")
		if estado:
			return Paquete.objects.filter(estado_actual__nombre=estado)
		return super().get_queryset()

class RutasPaqueteView(generics.ListAPIView):
	serializer_class = RutaSerializer

	def get_queryset(self):
		paquete_codigo = self.kwargs.get("codigo")
		return Ruta.objects.filter(paquete__codigo=paquete_codigo)
