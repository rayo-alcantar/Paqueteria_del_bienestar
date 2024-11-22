from django.shortcuts import render
from django.db import transaction
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
			return render(
				request,
				'rastreo_paquete.html',
				{
					"paquete": paquete,
					"rutas": rutas,
				},
			)
		except Paquete.DoesNotExist:
			error = "El número de rastreo ingresado no existe."
			return render(request, 'rastreo_paquete.html', {"error": error})
	return render(request, 'rastreo_paquete.html')  # Apunta a "templates/rastreo_paquete.html"

# Vista para solicitar envío
@transaction.atomic
def solicitar_envio(request):
	estados = Estado.objects.all()  # Recuperar todos los estados de la base de datos
	if request.method == "POST":
		try:
			descripcion = request.POST.get("descripcion")
			peso = request.POST.get("peso")
			remitente = request.POST.get("remitente")
			direccion_recoleccion = request.POST.get("direccion_recoleccion")
			receptor = request.POST.get("receptor")
			direccion_entrega = request.POST.get("direccion_entrega")
			estado_origen_id = request.POST.get("estado_origen_id")
			estado_destino_id = request.POST.get("estado_destino_id")

			# Validar entrada de datos
			if not all([descripcion, peso, remitente, direccion_recoleccion, receptor, direccion_entrega, estado_origen_id, estado_destino_id]):
				raise ValueError("Todos los campos son obligatorios.")

			peso = float(peso)
			if peso <= 0:
				raise ValueError("El peso del paquete debe ser un número positivo.")

			estado_origen = Estado.objects.get(pk=estado_origen_id)
			estado_destino = Estado.objects.get(pk=estado_destino_id)

			# Crear el paquete
			codigo = str(uuid.uuid4()).replace("-", "").upper()[:12]  # Código robusto
			paquete = Paquete.objects.create(
				codigo=codigo,
				remitente=remitente,
				direccion_recoleccion=direccion_recoleccion,
				receptor=receptor,
				direccion_entrega=direccion_entrega,
				descripcion=descripcion,
				peso=peso,
				estado_actual=estado_origen,
			)

			# Crear rutas iniciales
			frases = Frase.objects.all()
			Ruta.objects.create(
				paquete=paquete,
				frase=frases[0],  # Frase inicial (por ejemplo, "En recolección")
				estado_origen=estado_origen,
				estado_destino=estado_destino,
			)

			# Crear rutas intermedias si es necesario
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

			# Crear la ruta final
			Ruta.objects.create(
				paquete=paquete,
				frase=frases[2],  # Frase final (por ejemplo, "Entregado")
				estado_origen=estado_origen,
				estado_destino=estado_destino,
			)

			return render(
				request,
				'solicitar_envio.html',
				{
					"success": True,
					"codigo": paquete.codigo,
					"estado_origen": estado_origen.nombre,
					"estado_destino": estado_destino.nombre,
					"peso": paquete.peso,
					"descripcion": paquete.descripcion,
					"remitente": paquete.remitente,
					"direccion_recoleccion": paquete.direccion_recoleccion,
					"receptor": paquete.receptor,
					"direccion_entrega": paquete.direccion_entrega,
					"estados": estados,
				},
			)
		except Estado.DoesNotExist:
			error = "Alguno de los estados seleccionados no existe."
		except ValueError as ve:
			error = str(ve)
		except Exception as e:
			error = f"Hubo un error al procesar tu solicitud: {e}"
		return render(request, 'solicitar_envio.html', {"error": error, "estados": estados})

	return render(request, 'solicitar_envio.html', {"estados": estados})

# Vista "Acerca de"
def acerca_de(request):
	return render(request, 'acerca_de.html')  # Apunta a "templates/acerca_de.html"
