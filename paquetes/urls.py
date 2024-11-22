from django.urls import path
from . import views

urlpatterns = [
	# Rutas para los templates
	path('', views.index, name='index'),  # Página principal
	path('rastreo-paquete/', views.rastrear_paquete, name='rastreo_paquete'),  # Página de rastreo de paquete
	path('solicitar-envio/', views.solicitar_envio, name='solicitar_envio'),  # Página para solicitar envío
	path('acerca-de/', views.acerca_de, name='acerca_de'),  # Página "Acerca de"
]
