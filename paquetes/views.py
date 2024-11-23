import traceback
import random  # Importar el módulo random
from django.shortcuts import render, get_object_or_404
from django.db import transaction
from .models import Paquete, Estado, Ruta, Frase
from django.utils.timezone import now
from datetime import timedelta
import uuid

# Importaciones adicionales para generar PDFs
from django.http import HttpResponse
from django.template.loader import render_to_string
from io import BytesIO
from xhtml2pdf import pisa  # Asegúrate de instalar xhtml2pdf

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

			# Obtener estados de origen y destino
			estado_origen = rutas[0].estado_origen if rutas else None
			estado_destino = rutas[-1].estado_destino if rutas else None

			context = {
				"paquete": paquete,
				"rutas": rutas_relevantes,
				"estado_origen": estado_origen,
				"estado_destino": estado_destino,
			}

			# Si el paquete está entregado, generar PDF si se solicita
			if paquete.estado_paquete == "Entregado" and 'download_pdf' in request.POST:
				# Renderizar el template para el PDF
				pdf_content = render_to_string('paquete_entregado_pdf.html', context)
				response = HttpResponse(content_type='application/pdf')
				response['Content-Disposition'] = f'attachment; filename="paquete_{paquete.codigo}.pdf"'

				# Crear el PDF
				pisa_status = pisa.CreatePDF(
					pdf_content, dest=response
				)

				if pisa_status.err:
					return HttpResponse('Error al generar el PDF', status=500)
				return response

			return render(
				request,
				"rastreo_paquete.html",
				context,
			)

		except Paquete.DoesNotExist:
			error = "El número de rastreo ingresado no existe."
			return render(request, "rastreo_paquete.html", {"error": error})

	return render(request, "rastreo_paquete.html")

# Vista para solicitar envío
@transaction.atomic
def solicitar_envio(request):
	estados = Estado.objects.all()
	if request.method == "POST":
		errors = {}
		form_data = request.POST.copy()
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
			if not descripcion:
				errors['descripcion'] = "La descripción es obligatoria."
			if not peso:
				errors['peso'] = "El peso es obligatorio."
			else:
				try:
					peso = float(peso)
					if peso <= 0:
						errors['peso'] = "El peso debe ser un número positivo."
				except ValueError:
					errors['peso'] = "El peso debe ser un número válido."
			if not remitente:
				errors['remitente'] = "El nombre del remitente es obligatorio."
			if not direccion_recoleccion:
				errors['direccion_recoleccion'] = "La dirección de recolección es obligatoria."
			if not receptor:
				errors['receptor'] = "El nombre del receptor es obligatorio."
			if not direccion_entrega:
				errors['direccion_entrega'] = "La dirección de entrega es obligatoria."
			if not estado_origen_id:
				errors['estado_origen_id'] = "Debe seleccionar un estado de origen."
			if not estado_destino_id:
				errors['estado_destino_id'] = "Debe seleccionar un estado de destino."
			elif estado_origen_id == estado_destino_id:
				errors['estado_destino_id'] = "El estado de destino debe ser diferente al estado de origen."

			if errors:
				raise ValueError("Hay errores en el formulario.")

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
			if not frases.exists():
				raise Exception("No hay frases disponibles en la base de datos.")

			frases_list = list(frases)
			num_frases = len(frases_list)
			orden = 1
			rutas = []

			estados_ruta = [estado_origen]

			# Rutas intermedias
			if estado_origen.region != estado_destino.region:
				# Seleccionar estados intermedios lógicos
				estados_intermedios = list(Estado.objects.filter(
					region__in=["Centro", "Norte", "Sur"]
				).exclude(pk__in=[estado_origen.pk, estado_destino.pk]).distinct())

				if estados_intermedios:
					estado_intermedio = random.choice(estados_intermedios)
					estados_ruta.append(estado_intermedio)

			estados_ruta.append(estado_destino)

			# Crear rutas basadas en los estados de la ruta
			for i in range(len(estados_ruta) - 1):
				estado_origen_ruta = estados_ruta[i]
				estado_destino_ruta = estados_ruta[i + 1]
				frase_index = orden - 1 if orden - 1 < num_frases else num_frases - 1
				frase = frases_list[frase_index]
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
		except ValueError:
			# Enviamos los errores específicos al template
			return render(request, "solicitar_envio.html", {
				"errors": errors,
				"estados": estados,
				"form_data": form_data,
			})
		except Exception as e:
			error = f"Hubo un error al procesar tu solicitud: {e}"
			traceback_str = traceback.format_exc()
			print(traceback_str)  # Imprime el traceback en la consola para depuración
			return render(request, "solicitar_envio.html", {
				"error": error,
				"estados": estados,
				"form_data": form_data,
			})

	return render(request, "solicitar_envio.html", {"estados": estados})

# Vista "Acerca de"
def acerca_de(request):
	return render(request, "acerca_de.html")  # Apunta a "templates/acerca_de.html"
