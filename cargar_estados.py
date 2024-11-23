import unicodedata
from paquetes.models import Estado

# Función para eliminar acentos y asegurar codificación estándar
def eliminar_acentos_y_normalizar(texto):
    texto_sin_acentos = ''.join(
        c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn'
    )
    return texto_sin_acentos.encode('ascii', 'ignore').decode('utf-8')

# Datos de los estados organizados por región
estados_data = {
    "Norte": [
        {"estado": "Baja California", "latitud": 32.0},
        {"estado": "Sonora", "latitud": 29.0},
        {"estado": "Chihuahua", "latitud": 28.0},
        {"estado": "Coahuila", "latitud": 27.0},
        {"estado": "Nuevo Leon", "latitud": 25.7},
        {"estado": "Tamaulipas", "latitud": 24.2},
        {"estado": "Baja California Sur", "latitud": 24.0},
        {"estado": "Sinaloa", "latitud": 24.0},
        {"estado": "Durango", "latitud": 24.0},
        {"estado": "Zacatecas", "latitud": 22.8},
        {"estado": "San Luis Potosi", "latitud": 22.2},
        {"estado": "Aguascalientes", "latitud": 21.9},
        {"estado": "Nayarit", "latitud": 21.5},
    ],
    "Centro": [
        {"estado": "Guanajuato", "latitud": 21.0},
        {"estado": "Queretaro", "latitud": 20.6},
        {"estado": "Jalisco", "latitud": 20.5},
        {"estado": "Yucatan", "latitud": 20.4},
        {"estado": "Hidalgo", "latitud": 20.1},
        {"estado": "Campeche", "latitud": 19.8},
        {"estado": "Michoacan", "latitud": 19.7},
        {"estado": "Ciudad de Mexico", "latitud": 19.4},
        {"estado": "Estado de Mexico", "latitud": 19.3},
        {"estado": "Tlaxcala", "latitud": 19.3},
        {"estado": "Colima", "latitud": 19.2},
        {"estado": "Veracruz", "latitud": 19.2},
        {"estado": "Puebla", "latitud": 19.0},
        {"estado": "Morelos", "latitud": 18.9},
        {"estado": "Tabasco", "latitud": 18.0},
        {"estado": "Quintana Roo", "latitud": 19.0},
    ],
    "Sur": [
        {"estado": "Guerrero", "latitud": 17.6},
        {"estado": "Oaxaca", "latitud": 17.1},
        {"estado": "Chiapas", "latitud": 16.5},
    ],
}

# Paso 1: Eliminar todos los estados existentes
print("Eliminando todos los estados existentes...")
Estado.objects.all().delete()

# Paso 2: Crear estados en la base de datos
print("Cargando nuevos estados...")
for region, estados in estados_data.items():
    for estado in estados:
        Estado.objects.update_or_create(
            nombre=eliminar_acentos_y_normalizar(estado["estado"]),  # Nombre sin acentos ni problemas de codificación
            defaults={
                "latitud": estado["latitud"],
                "region": region,
            },
        )

import unicodedata
from paquetes.models import Estado

# Función para eliminar acentos y asegurar codificación estándar
def eliminar_acentos_y_normalizar(texto):
    texto_sin_acentos = ''.join(
        c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn'
    )
    return texto_sin_acentos.encode('ascii', 'ignore').decode('utf-8')

# Datos de los estados organizados por región
estados_data = {
    "Norte": [
        {"estado": "Baja California", "latitud": 32.0},
        {"estado": "Sonora", "latitud": 29.0},
        {"estado": "Chihuahua", "latitud": 28.0},
        {"estado": "Coahuila", "latitud": 27.0},
        {"estado": "Nuevo Leon", "latitud": 25.7},
        {"estado": "Tamaulipas", "latitud": 24.2},
        {"estado": "Baja California Sur", "latitud": 24.0},
        {"estado": "Sinaloa", "latitud": 24.0},
        {"estado": "Durango", "latitud": 24.0},
        {"estado": "Zacatecas", "latitud": 22.8},
        {"estado": "San Luis Potosi", "latitud": 22.2},
        {"estado": "Aguascalientes", "latitud": 21.9},
        {"estado": "Nayarit", "latitud": 21.5},
    ],
    "Centro": [
        {"estado": "Guanajuato", "latitud": 21.0},
        {"estado": "Queretaro", "latitud": 20.6},
        {"estado": "Jalisco", "latitud": 20.5},
        {"estado": "Yucatan", "latitud": 20.4},
        {"estado": "Hidalgo", "latitud": 20.1},
        {"estado": "Campeche", "latitud": 19.8},
        {"estado": "Michoacan", "latitud": 19.7},
        {"estado": "Ciudad de Mexico", "latitud": 19.4},
        {"estado": "Estado de Mexico", "latitud": 19.3},
        {"estado": "Tlaxcala", "latitud": 19.3},
        {"estado": "Colima", "latitud": 19.2},
        {"estado": "Veracruz", "latitud": 19.2},
        {"estado": "Puebla", "latitud": 19.0},
        {"estado": "Morelos", "latitud": 18.9},
        {"estado": "Tabasco", "latitud": 18.0},
        {"estado": "Quintana Roo", "latitud": 19.0},
    ],
    "Sur": [
        {"estado": "Guerrero", "latitud": 17.6},
        {"estado": "Oaxaca", "latitud": 17.1},
        {"estado": "Chiapas", "latitud": 16.5},
    ],
}

# Paso 1: Eliminar todos los estados existentes
print("Eliminando todos los estados existentes...")
Estado.objects.all().delete()

# Paso 2: Crear estados en la base de datos
print("Cargando nuevos estados...")
for region, estados in estados_data.items():
    for estado in estados:
        Estado.objects.update_or_create(
            nombre=eliminar_acentos_y_normalizar(estado["estado"]),  # Nombre sin acentos ni problemas de codificación
            defaults={
                "latitud": estado["latitud"],
                "region": region,
            },
        )

print("Estados cargados exitosamente.")
print("Estados cargados exitosamente.")
