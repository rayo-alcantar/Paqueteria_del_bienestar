from django.contrib import admin
from django.urls import path, include
from paquetes import views  # Importamos las vistas de la app paquetes

urlpatterns = [
	path('admin/', admin.site.urls),
	path('', views.index, name='index'),  # Ruta para la página principal
	path('rastreo/', views.rastrear_paquete, name='rastreo-paquete'),  # Ruta para rastrear paquetes
	path('solicitar/', views.solicitar_envio, name='solicitar-envio'),  # Ruta para solicitar envío
	path('acerca-de/', views.acerca_de, name='acerca-de'),  # Ruta para la página "acerca de"
	path('api/', include('paquetes.urls')),  # Mantiene las rutas de la API bajo el prefijo "api/"
]
