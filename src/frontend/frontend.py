import requests

def get_consumers(region=None, nivel_consumo=None):
    """Obtiene la lista de consumidores con filtros opcionales."""
    url = 'http://localhost:5000/api/consumidores'
    params = {}

    # Agregar filtros si están definidos
    if region:
        params['region'] = region
    if nivel_consumo:
        params['nivel_consumo'] = nivel_consumo

    try:
        # Hacer la solicitud GET al endpoint
        response = requests.get(url, params=params)
        response.raise_for_status()  # Lanza una excepción si el código de estado no es 200
        
        # Procesar la respuesta JSON
        data = response.json()
        print("Consumidores obtenidos:", data['data'])
        print("Total de consumidores:", data['total'])
        
        return data['data']
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener consumidores: {e}")
        return None

# Ejemplo de uso
get_consumers(region='Madrid', nivel_consumo='alto')
def get_consumer_details(consumer_id):
    """Obtiene los detalles de un consumidor específico por su ID."""
    url = f'http://localhost:5000/api/consumidores/{consumer_id}'

    try:
        # Hacer la solicitud GET al endpoint
        response = requests.get(url)
        response.raise_for_status()  # Lanza una excepción si el código de estado no es 200
        
        # Procesar la respuesta JSON
        data = response.json()
        print("Detalles del consumidor:", data['data'])
        
        return data['data']
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener detalles del consumidor: {e}")
        return None

# Ejemplo de uso
get_consumer_details(1)
def get_consumption_by_region():
    """Obtiene el análisis de consumo por región."""
    url = 'http://localhost:5000/api/analytics/consumo-por-region'

    try:
        # Hacer la solicitud GET al endpoint
        response = requests.get(url)
        response.raise_for_status()  # Lanza una excepción si el código de estado no es 200
        
        # Procesar la respuesta JSON
        data = response.json()
        print("Análisis de consumo por región:")
        
        for region, stats in data['data'].items():
            print(f"Región: {region}")
            print(f"  Media: {stats['gasto_mensual']['mean']}")
            print(f"  Mínimo: {stats['gasto_mensual']['min']}")
            print(f"  Máximo: {stats['gasto_mensual']['max']}")
            print(f"  Total: {stats['gasto_mensual']['count']}")
        
        return data['data']
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener análisis de consumo: {e}")
        return None

# Ejemplo de uso
get_consumption_by_region()
