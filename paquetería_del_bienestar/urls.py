from django.contrib import admin
from django.urls import path, include

urlpatterns = [
	path('admin/', admin.site.urls),
	path('api/', include('paquetes.urls')),  # Agregamos las rutas de la app paquetes bajo el prefijo "api/"
]
