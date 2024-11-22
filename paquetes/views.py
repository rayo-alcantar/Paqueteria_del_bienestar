from django.shortcuts import render, get_object_or_404
from django.db import transaction
from .models import Paquete, Estado, Ruta, Frase
from django.utils.timezone import now
from datetime import timedelta
import uuid


# Vista para la página principal
def index(request):
	return render(request, 'index.html')  # Apunta a "templates/index.html"


# Vista para rastrear paquete
def rastrear_paquete(request):
	if request.method == "POST":
		codigo = request.POST.get("codigo")
		try:
			paquete = get_object_or_404(Paquete, codigo=codigo)
			rutas = list(Ruta.objects.filter(paquete=paquete).order_by("orden"))

			# Identificar la ruta activa actual
			ruta_actual = next((ruta for ruta in rutas if ruta.activo), None)

			if ruta_actual:
				# Desactivar la ruta actual
				ruta_actual.activo = False
				ruta_actual.save()

				# Buscar la siguiente ruta en la lista
				siguiente_ruta = next((ruta for ruta in rutas if ruta.orden > ruta_actual.orden), None)

				if siguiente_ruta:
					# Calcular tiempo de transición basado en distancia ficticia
					distancia_ficticia = (
						abs(siguiente_ruta.estado_origen.latitud - siguiente_ruta.estado_destino.latitud) +
						abs(siguiente_ruta.estado_origen.longitud - siguiente_ruta.estado_destino.longitud)
					)
					tiempo_transicion = timedelta(minutes=5 + distancia_ficticia * 5)

					# Activar la siguiente ruta solo si ha pasado el tiempo de transición
					if now() >= ruta_actual.fecha_actualizacion + tiempo_transicion:
						siguiente_ruta.activo = True
						siguiente_ruta.fecha_actualizacion = now()
						siguiente_ruta.save()

						# Actualizar el estado del paquete
						paquete.estado_actual = siguiente_ruta.estado_destino
						paquete.save()
				else:
					# Si no hay más rutas, marcar el paquete como entregado
					paquete.estado_paquete = "Entregado"
					paquete.fecha_entrega = now()
					paquete.save()

			else:
				# Si no hay ruta activa, activar la primera
				primera_ruta = rutas[0] if rutas else None
				if primera_ruta:
					primera_ruta.activo = True
					primera_ruta.fecha_actualizacion = now()
					primera_ruta.save()

			return render(
				request,
				"rastreo_paquete.html",
				{
					"paquete": paquete,
					"rutas": rutas,
				},
			)

		except Paquete.DoesNotExist:
			error = "El número de rastreo ingresado no existe."
			return render(request, "rastreo_paquete.html", {"error": error})

	return render(request, "rastreo_paquete.html")


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

			estado_origen = get_object_or_404(Estado, pk=estado_origen_id)
			estado_destino = get_object_or_404(Estado, pk=estado_destino_id)

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

			# Crear rutas
			frases = Frase.objects.all()
			orden = 1

			# Ruta inicial
			Ruta.objects.create(
				paquete=paquete,
				frase=frases[0],  # Frase inicial
				estado_origen=estado_origen,
				estado_destino=estado_origen,  # Misma dirección para comenzar
				orden=orden,
				activo=True,  # Primera ruta activa de inmediato
			)
			orden += 1

			# Rutas intermedias y final
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
						orden=orden,
					)
					orden += 1

			# Ruta final
			Ruta.objects.create(
				paquete=paquete,
				frase=frases[2],  # Frase final
				estado_origen=estado_destino,
				estado_destino=estado_destino,
				orden=orden,
			)

			return render(
				request,
				"solicitar_envio.html",
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
		return render(request, "solicitar_envio.html", {"error": error, "estados": estados})

	return render(request, "solicitar_envio.html", {"estados": estados})


# Vista "Acerca de"
def acerca_de(request):
	return render(request, "acerca_de.html")  # Apunta a "templates/acerca_de.html"
