from django.urls import path
from . import views
from .views import (
    CrearPaqueteView,
    DetallePaqueteView,
    ListarPaquetesView,
    RutasPaqueteView,
)

urlpatterns = [
    # Rutas del backend
    path("paquetes/", CrearPaqueteView.as_view(), name="crear-paquete"),
    path("paquetes/<str:codigo>/", DetallePaqueteView.as_view(), name="detalle-paquete"),
    path("paquetes/listar/", ListarPaquetesView.as_view(), name="listar-paquetes"),
    path("paquetes/<str:codigo>/rutas/", RutasPaqueteView.as_view(), name="rutas-paquete"),
    
    # Rutas para los templates
    path('', views.index, name='index'),  # Página principal
    path('rastreo-paquete/', views.rastrear_paquete, name='rastreo-paquete'),  # Página de rastreo de paquete
    path('solicitar-envio/', views.solicitar_envio, name='solicitar-envio'),  # Página para solicitar envío
    path('acerca-de/', views.acerca_de, name='acerca-de'),  # Página "Acerca de"
]
