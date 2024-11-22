from django.shortcuts import render
from .models import Paquete, Estado, Ruta, Frase
import uuid

# Vista para la página principal
def index(request):
	return render(request, 'index.html')  # Apunta a "templates/index.html"

# Vista para rastrear paquete
def rastrear_paquete(request):
	if request.method == "POST":
		codigo = request.POST.get("codigo")
		try:
			paquete = Paquete.objects.get(codigo=codigo)
			rutas = Ruta.objects.filter(paquete=paquete)
			return render(request, 'rastreo_paquete.html', {"paquete": paquete, "rutas": rutas})
		except Paquete.DoesNotExist:
			error = "El número de rastreo ingresado no existe."
			return render(request, 'rastreo_paquete.html', {"error": error})
	return render(request, 'rastreo_paquete.html')  # Apunta a "templates/rastreo_paquete.html"

# Vista para solicitar envío
def solicitar_envio(request):
	estados = Estado.objects.all()  # Recuperar todos los estados de la base de datos
	if request.method == "POST":
		descripcion = request.POST.get("descripcion")
		peso = request.POST.get("peso")
		estado_origen_id = request.POST.get("estado_origen_id")
		estado_destino_id = request.POST.get("estado_destino_id")

		try:
			# Validar entrada de datos
			if not all([descripcion, peso, estado_origen_id, estado_destino_id]):
				raise ValueError("Todos los campos son obligatorios.")
			
			estado_origen = Estado.objects.get(pk=estado_origen_id)
			estado_destino = Estado.objects.get(pk=estado_destino_id)
			codigo = str(uuid.uuid4()).replace("-", "").upper()[:10]  # Código robusto
			
			# Crear el paquete
			paquete = Paquete.objects.create(
				codigo=codigo,
				descripcion=descripcion,
				peso=float(peso),
				estado_actual=estado_origen,
			)

			# Crear rutas
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

			# Retornar datos del paquete y el código generado
			return render(
				request,
				'solicitar_envio.html',
				{
					"codigo": paquete.codigo,
					"estado_origen": estado_origen.nombre,
					"estado_destino": estado_destino.nombre,
					"peso": paquete.peso,
					"descripcion": paquete.descripcion,
					"success": True,
					"estados": estados,
				},
			)
		except Estado.DoesNotExist:
			error = "Alguno de los estados seleccionados no existe."
			return render(request, 'solicitar_envio.html', {"error": error, "estados": estados})
		except ValueError as ve:
			return render(request, 'solicitar_envio.html', {"error": str(ve), "estados": estados})
		except Exception as e:
			error = f"Hubo un error al procesar tu solicitud: {e}"
			return render(request, 'solicitar_envio.html', {"error": error, "estados": estados})

	return render(request, 'solicitar_envio.html', {"estados": estados})  # Incluye los estados siempre

# Vista "Acerca de"
def acerca_de(request):
	return render(request, 'acerca_de.html')  # Apunta a "templates/acerca_de.html"
