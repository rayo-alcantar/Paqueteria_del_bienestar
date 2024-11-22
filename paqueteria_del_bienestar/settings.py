from pathlib import Path

# Construye rutas dentro del proyecto como BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Clave secreta (mantenla en secreto en producción)
SECRET_KEY = '95gz=npbnhkvqss#bk-db_by#mz+*$xzeai9n$e0ww$i_v2y1%'

# ¡No ejecutes con debug activado en producción!
DEBUG = True

ALLOWED_HOSTS = []

# Definición de aplicaciones
INSTALLED_APPS = [
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	'paquetes',  # Tu app de paquetes
]

MIDDLEWARE = [
	'django.middleware.security.SecurityMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Evita usar caracteres especiales en nombres de módulos
ROOT_URLCONF = 'paqueteria_del_bienestar.urls'

# Configuración de plantillas
TEMPLATES = [
	{
		'BACKEND': 'django.template.backends.django.DjangoTemplates',
		'DIRS': [BASE_DIR / 'templates'],  # Ruta global al directorio de plantillas
		'APP_DIRS': True,
		'OPTIONS': {
			'context_processors': [
				'django.template.context_processors.debug',
				'django.template.context_processors.request',
				'django.contrib.auth.context_processors.auth',
				'django.contrib.messages.context_processors.messages',
			],
		},
	},
]

# Evita usar caracteres especiales en nombres de módulos
WSGI_APPLICATION = 'paqueteria_del_bienestar.wsgi.application'

# Configuración de la base de datos
DATABASES = {
	'default': {
		'ENGINE': 'djongo',
		'NAME': 'paqueteria_mexicana',  # Nombre de tu base en MongoDB
		'HOST': 'localhost',			# MongoDB local
		'PORT': 27017,				  # Puerto estándar de MongoDB
	}
}

# Validación de contraseñas
AUTH_PASSWORD_VALIDATORS = [
	{
		'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
	},
	{
		'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
	},
	{
		'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
	},
	{
		'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
	},
]

# Internacionalización
LANGUAGE_CODE = 'es-mx'  # Ajustado para México

TIME_ZONE = 'America/Mexico_City'  # Zona horaria de México

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Archivos estáticos (CSS, JavaScript, Imágenes)
STATIC_URL = '/static/'  # Debe ser una cadena, no una lista

STATICFILES_DIRS = [
	BASE_DIR / "static",  # Si tienes una carpeta 'static' en la raíz del proyecto
]
from pathlib import Path

# Construye rutas dentro del proyecto como BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Clave secreta (mantenla en secreto en producción)
SECRET_KEY = '95gz=npbnhkvqss#bk-db_by#mz+*$xzeai9n$e0ww$i_v2y1%'

# ¡No ejecutes con debug activado en producción!
DEBUG = True

ALLOWED_HOSTS = []

# Definición de aplicaciones
INSTALLED_APPS = [
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	'paquetes',  # Tu app de paquetes
]

MIDDLEWARE = [
	'django.middleware.security.SecurityMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Evita usar caracteres especiales en nombres de módulos
ROOT_URLCONF = 'paqueteria_del_bienestar.urls'

# Configuración de plantillas
TEMPLATES = [
	{
		'BACKEND': 'django.template.backends.django.DjangoTemplates',
		'DIRS': [BASE_DIR / 'templates'],  # Ruta global al directorio de plantillas
		'APP_DIRS': True,
		'OPTIONS': {
			'context_processors': [
				'django.template.context_processors.debug',
				'django.template.context_processors.request',
				'django.contrib.auth.context_processors.auth',
				'django.contrib.messages.context_processors.messages',
			],
		},
	},
]

# Evita usar caracteres especiales en nombres de módulos
WSGI_APPLICATION = 'paqueteria_del_bienestar.wsgi.application'

# Configuración de la base de datos
DATABASES = {
	'default': {
		'ENGINE': 'djongo',
		'NAME': 'paqueteria_mexicana',  # Nombre de tu base en MongoDB
		'HOST': 'localhost',			# MongoDB local
		'PORT': 27017,				  # Puerto estándar de MongoDB
	}
}

# Validación de contraseñas
AUTH_PASSWORD_VALIDATORS = [
	{
		'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
	},
	{
		'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
	},
	{
		'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
	},
	{
		'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
	},
]

# Internacionalización
LANGUAGE_CODE = 'es-mx'  # Ajustado para México

TIME_ZONE = 'America/Mexico_City'  # Zona horaria de México

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Archivos estáticos (CSS, JavaScript, Imágenes)
STATIC_URL = '/static/'  # Debe ser una cadena, no una lista

STATICFILES_DIRS = [
	BASE_DIR / "static",  # Si tienes una carpeta 'static' en la raíz del proyecto
]
REST_FRAMEWORK = {
	'DEFAULT_RENDERER_CLASSES': (
		'rest_framework.renderers.JSONRenderer',  # Renderizar siempre en JSON
	),
	'DEFAULT_PARSER_CLASSES': (
		'rest_framework.parsers.JSONParser',
	),
}
