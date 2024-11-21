from django.urls import path
from . import views
from .views import (
	CrearPaqueteView,
	DetallePaqueteView,
	ListarPaquetesView,
	RutasPaqueteView,
)

urlpatterns = [
	# Rutas del backend (API)
	path("api/paquetes/", CrearPaqueteView.as_view(), name="crear-paquete"),
	path("api/paquetes/<str:codigo>/", DetallePaqueteView.as_view(), name="detalle-paquete"),
	path("api/paquetes/listar/", ListarPaquetesView.as_view(), name="listar-paquetes"),
	path("api/paquetes/<str:codigo>/rutas/", RutasPaqueteView.as_view(), name="rutas-paquete"),
	
	# Rutas para los templates
	path('', views.index, name='index'),  # Página principal
	path('rastreo-paquete/', views.rastrear_paquete, name='rastreo_paquete'),  # Página de rastreo de paquete
	path('solicitar-envio/', views.solicitar_envio, name='solicitar_envio'),  # Página para solicitar envío
	path('acerca-de/', views.acerca_de, name='acerca_de'),  # Página "Acerca de"
]
