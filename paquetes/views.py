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
				siguiente_ruta = next((ruta for ruta in rutas if ruta.orden > ruta_actual.orden), None)

				# Calcular tiempo de transición entre rutas
				tiempo_transicion = timedelta(minutes=1)  # Reducir a 1 minuto para acelerar la transición

				# Activar la siguiente ruta si el tiempo ha pasado
				if now() >= ruta_actual.fecha_actualizacion + tiempo_transicion:
					ruta_actual.activo = False
					ruta_actual.save()

					if siguiente_ruta:
						siguiente_ruta.activo = True
						siguiente_ruta.fecha_actualizacion = now()
						siguiente_ruta.save()

						# Actualizar el estado del paquete
						paquete.estado_actual = siguiente_ruta.estado_destino
					else:
						# No hay más rutas, paquete entregado
						paquete.estado_paquete = "Entregado"
						paquete.fecha_entrega = now()

					paquete.save()
			else:
				# Si no hay ruta activa y el paquete no está entregado, activamos la primera ruta
				if paquete.estado_paquete != "Entregado":
					primera_ruta = rutas[0] if rutas else None
					if primera_ruta:
						primera_ruta.activo = True
						primera_ruta.fecha_actualizacion = now()
						primera_ruta.save()
						paquete.estado_actual = primera_ruta.estado_destino
						paquete.save()

			# Filtrar rutas para mostrar solo las activas y anteriores
			if paquete.estado_paquete == "Entregado":
				rutas_relevantes = rutas
			else:
				rutas_relevantes = [ruta for ruta in rutas if ruta.fecha_actualizacion]

			return render(
				request,
				"rastreo_paquete.html",
				{
					"paquete": paquete,
					"rutas": rutas_relevantes,
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
			codigo = str(uuid.uuid4()).replace("-", "").upper()[:12]
			paquete = Paquete.objects.create(
				codigo=codigo,
				remitente=remitente,
				direccion_recoleccion=direccion_recoleccion,
				receptor=receptor,
				direccion_entrega=direccion_entrega,
				descripcion=descripcion,
				peso=peso,
				estado_actual=estado_origen,
				estado_paquete="En tránsito",  # Establecer estado inicial
			)

			# Crear rutas realistas
			frases = Frase.objects.all()
			orden = 1
			rutas = []

			estados_ruta = [estado_origen]

			# Rutas intermedias
			if estado_origen.region != estado_destino.region:
				# Seleccionar estados intermedios lógicos
				estados_intermedios = Estado.objects.filter(
					region__in=["Centro", "Norte", "Sur"]
				).exclude(pk__in=[estado_origen.pk, estado_destino.pk]).distinct().order_by('?')[:1]  # Limitar a 1 estado intermedio aleatorio

				estados_ruta.extend(estados_intermedios)
			estados_ruta.append(estado_destino)

			# Crear rutas basadas en los estados de la ruta
			for i in range(len(estados_ruta) - 1):
				estado_origen_ruta = estados_ruta[i]
				estado_destino_ruta = estados_ruta[i + 1]
				frase = frases[orden - 1] if orden - 1 < len(frases) else frases.last()
				ruta = Ruta(
					paquete=paquete,
					frase=frase,
					estado_origen=estado_origen_ruta,
					estado_destino=estado_destino_ruta,
					orden=orden,
					activo=(orden == 1),  # Solo la primera ruta activa
					fecha_actualizacion=now() if orden == 1 else None,
				)
				rutas.append(ruta)
				orden += 1

			Ruta.objects.bulk_create(rutas)

			return render(
				request,
				"solicitar_envio.html",
				{
					"success": True,
					"codigo": paquete.codigo,
					"estado_origen": paquete.estado_actual.nombre,
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
