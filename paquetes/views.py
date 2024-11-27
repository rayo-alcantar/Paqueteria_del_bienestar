import traceback
import random
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

# Mapeo de tiempo de transición por tipo de ruta (2 minutos para cada transición)
TIEMPO_TRANSICION_MAP = {
	"Recolección": timedelta(minutes=1),
	"En Tránsito": timedelta(minutes=1),
	"En Centro de Distribución": timedelta(minutes=1),
	"En Entrega": timedelta(minutes=1),
	# Puedes ajustar estos tiempos según necesidad
}

# Orden lógico de regiones para facilitar la selección de rutas
REGION_ORDER = ["Norte", "Centro", "Sur"]

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
				# Determinar el tipo de ruta basado en el orden
				tipo_ruta = "Recolección" if ruta_actual.orden == 1 else "En Tránsito"

				tiempo_transicion = TIEMPO_TRANSICION_MAP.get(tipo_ruta, timedelta(minutes=2))

				siguiente_ruta = next((ruta for ruta in rutas if ruta.orden > ruta_actual.orden), None)

				# Activar la siguiente ruta si el tiempo ha pasado
				if now() >= ruta_actual.fecha_actualizacion + tiempo_transicion:
					ruta_actual.activo = False
					ruta_actual.save()

					if siguiente_ruta:
						siguiente_ruta.activo = True
						siguiente_ruta.fecha_actualizacion = now()
						siguiente_ruta.save()

						# Actualizar el estado del paquete a "En Tránsito"
						paquete.estado_actual = siguiente_ruta.estado_destino
						paquete.estado_paquete = "En Tránsito"
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
						paquete.estado_paquete = "Recolección"
						paquete.save()

			# Filtrar rutas para mostrar solo las completadas y la activa
			if paquete.estado_paquete == "Entregado":
				rutas_relevantes = rutas
			else:
				rutas_relevantes = [ruta for ruta in rutas if ruta.fecha_actualizacion or ruta.activo]

			# Obtener estados de origen y destino
			estado_origen = rutas[0].estado_origen if rutas else None
			estado_destino = rutas[-1].estado_destino if rutas else None

			context = {
				"paquete": paquete,
				"rutas": rutas_relevantes,
				"estado_origen": estado_origen,
				"estado_destino": estado_destino,
			}

			return render(
				request,
				"rastreo_paquete.html",
				context,
			)

		except Paquete.DoesNotExist:
			error = "El número de rastreo ingresado no existe."
			return render(request, "rastreo_paquete.html", {"error": error})

	return render(request, "rastreo_paquete.html")

# Nueva vista para descargar el PDF
def descargar_pdf(request, codigo):
	try:
		paquete = get_object_or_404(Paquete, codigo=codigo)
		rutas = list(Ruta.objects.filter(paquete=paquete).order_by("orden"))
		estado_origen = rutas[0].estado_origen if rutas else None
		estado_destino = rutas[-1].estado_destino if rutas else None

		context = {
			"paquete": paquete,
			"rutas": rutas,
			"estado_origen": estado_origen,
			"estado_destino": estado_destino,
		}

		# Renderizar el template para el PDF
		pdf_content = render_to_string('paquete_entregado_pdf.html', context)
		response = HttpResponse(content_type='application/pdf')
		response['Content-Disposition'] = f'attachment; filename="comprobante_entrega_{paquete.codigo}.pdf"'

		# Crear el PDF
		pisa_status = pisa.CreatePDF(
			pdf_content, dest=response
		)

		if pisa_status.err:
			return HttpResponse('Error al generar el PDF', status=500)
		return response

	except Exception as e:
		error = f"Hubo un error al generar el PDF: {e}"
		traceback_str = traceback.format_exc()
		print(traceback_str)  # Imprime el traceback en la consola para depuración
		# Re-renderizar la página de rastreo con el error
		rutas = list(Ruta.objects.filter(paquete=paquete).order_by("orden")) if 'paquete' in locals() else []
		estado_origen = rutas[0].estado_origen if rutas else None
		estado_destino = rutas[-1].estado_destino if rutas else None

		context = {
			"error": error,
			"paquete": paquete,
			"rutas": rutas,
			"estado_origen": estado_origen,
			"estado_destino": estado_destino,
		}
		return render(request, "rastreo_paquete.html", context)

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

			# Datos de dirección de recolección
			colonia_recoleccion = request.POST.get("colonia_recoleccion")
			calle_recoleccion = request.POST.get("calle_recoleccion")
			numero_recoleccion = request.POST.get("numero_recoleccion")
			codigo_postal_recoleccion = request.POST.get("codigo_postal_recoleccion")

			receptor = request.POST.get("receptor")

			# Datos de dirección de entrega
			colonia_entrega = request.POST.get("colonia_entrega")
			calle_entrega = request.POST.get("calle_entrega")
			numero_entrega = request.POST.get("numero_entrega")
			codigo_postal_entrega = request.POST.get("codigo_postal_entrega")

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

			# Validar dirección de recolección
			if not colonia_recoleccion:
				errors['colonia_recoleccion'] = "La colonia de recolección es obligatoria."
			if not calle_recoleccion:
				errors['calle_recoleccion'] = "La calle de recolección es obligatoria."
			if not numero_recoleccion:
				errors['numero_recoleccion'] = "El número de recolección es obligatorio."
			if not codigo_postal_recoleccion:
				errors['codigo_postal_recoleccion'] = "El código postal de recolección es obligatorio."

			if not receptor:
				errors['receptor'] = "El nombre del receptor es obligatorio."

			# Validar dirección de entrega
			if not colonia_entrega:
				errors['colonia_entrega'] = "La colonia de entrega es obligatoria."
			if not calle_entrega:
				errors['calle_entrega'] = "La calle de entrega es obligatoria."
			if not numero_entrega:
				errors['numero_entrega'] = "El número de entrega es obligatorio."
			if not codigo_postal_entrega:
				errors['codigo_postal_entrega'] = "El código postal de entrega es obligatorio."

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

			# Concatenar direcciones
			direccion_recoleccion = f"{calle_recoleccion} {numero_entrega}, Col. {colonia_recoleccion}, C.P. {codigo_postal_recoleccion}"
			direccion_entrega = f"{calle_entrega} {numero_entrega}, Col. {colonia_entrega}, C.P. {codigo_postal_entrega}"

			# Crear el paquete con estado inicial "Recolección"
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
				estado_paquete="Recolección",  # Establecer estado inicial en "Recolección"
			)

			# Crear rutas realistas
			frases = Frase.objects.all()
			if not frases.exists():
				raise Exception("No hay frases disponibles en la base de datos.")

			frases_list = list(frases)
			orden = 1
			rutas = []

			estados_ruta = [estado_origen]

			# Ruta 1: Recolección
			frase_recoleccion = random.choice(frases_list)
			ruta_recoleccion = Ruta(
				paquete=paquete,
				frase=frase_recoleccion,
				estado_origen=estado_origen,
				estado_destino=estado_origen,  # Recolección en el mismo estado de origen
				orden=orden,
				activo=True,  # Primera ruta activa
				fecha_actualizacion=now(),
			)
			rutas.append(ruta_recoleccion)
			orden += 1

			# Rutas intermedias basadas en la dirección geográfica
			if estado_origen.region != estado_destino.region:
				# Determinar la dirección de la región
				origen_idx = REGION_ORDER.index(estado_origen.region) if estado_origen.region in REGION_ORDER else -1
				destino_idx = REGION_ORDER.index(estado_destino.region) if estado_destino.region in REGION_ORDER else -1

				if origen_idx == -1 or destino_idx == -1:
					# Si alguna región no está en el orden, seleccionar intermedios aleatorios
					estados_intermedios = list(Estado.objects.filter(
						region__in=REGION_ORDER
					).exclude(pk__in=[estado_origen.pk, estado_destino.pk]).distinct())
				elif origen_idx < destino_idx:
					# Mover hacia el sur
					regiones_intermedias = REGION_ORDER[origen_idx + 1: destino_idx]
					estados_intermedios = list(Estado.objects.filter(
						region__in=regiones_intermedias
					).exclude(pk__in=[estado_origen.pk, estado_destino.pk]).distinct())
				else:
					# Mover hacia el norte
					regiones_intermedias = REGION_ORDER[destino_idx + 1: origen_idx]
					estados_intermedios = list(Estado.objects.filter(
						region__in=regiones_intermedias
					).exclude(pk__in=[estado_origen.pk, estado_destino.pk]).distinct())

				# Seleccionar hasta 2 estados intermedios para mayor realismo
				if estados_intermedios:
					num_intermedias = min(2, len(estados_intermedios))
					estados_seleccionados = random.sample(estados_intermedios, num_intermedias)
					estados_ruta.extend(estados_seleccionados)

			estados_ruta.append(estado_destino)

			# Crear rutas basadas en los estados de la ruta
			for i in range(len(estados_ruta) - 1):
				estado_origen_ruta = estados_ruta[i]
				estado_destino_ruta = estados_ruta[i + 1]
				frase = random.choice(frases_list)
				ruta = Ruta(
					paquete=paquete,
					frase=frase,
					estado_origen=estado_origen_ruta,
					estado_destino=estado_destino_ruta,
					orden=orden,
					activo=False,  # Solo la primera ruta (Recolección) está activa
					fecha_actualizacion=None,
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
					"direccion_recoleccion": direccion_recoleccion,
					"receptor": paquete.receptor,
					"direccion_entrega": direccion_entrega,
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

# Vista FAQ
def FAQ(request):
	return render(request, "FAQ.html")  # Apunta a "templates/faq.html"
