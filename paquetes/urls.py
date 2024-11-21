from django.urls import path
from .views import (
	CrearPaqueteView,
	DetallePaqueteView,
	ListarPaquetesView,
	RutasPaqueteView,
)

urlpatterns = [
	path("paquetes/", CrearPaqueteView.as_view(), name="crear-paquete"),
	path("paquetes/<str:codigo>/", DetallePaqueteView.as_view(), name="detalle-paquete"),
	path("paquetes/listar/", ListarPaquetesView.as_view(), name="listar-paquetes"),
	path("paquetes/<str:codigo>/rutas/", RutasPaqueteView.as_view(), name="rutas-paquete"),
]
