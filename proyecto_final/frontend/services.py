"""
Capa de servicios del frontend.

Aquí se define la comunicación con el backend (la API de FastAPI de la
Sección 2). La app de Gradio (app.py) no sabe nada de HTTP: solo llama a
`enviar_prediccion` y recibe de vuelta el nivel de prioridad.
"""

import os

import requests

# La URL del backend se obtiene de una variable de ambiente. En local,
# por defecto apunta a localhost; dentro de docker-compose
# se le pasa BACKEND_URL=http://backend:8000 a nivel de contenedor.
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")
PREDICT_ENDPOINT = f"{BACKEND_URL.rstrip('/')}/predict"

# El modelo puede tardar unos segundos (llama a la API de embeddings de Google),
# así que damos un timeout holgado.
TIMEOUT_S = 60


def enviar_prediccion(asunto: str, contenido: str) -> str:
    """
    Envía el asunto y el contenido del ticket al endpoint /predict del backend
    y devuelve el Nivel_Prioridad predicho ('Baja', 'Media', 'Alta' o 'Critica').

    Nota de diseño: el modelo desplegado clasifica la prioridad únicamente a
    partir del texto del ticket (asunto + contenido), por lo que solo esos dos
    campos se envían a la API. El resto de atributos del formulario se recogen
    para una interfaz más realista, pero no forman parte de la request.

    Lanza requests.exceptions.RequestException si la llamada falla (la maneja
    quien llama, en app.py).
    """
    payload = {"asunto": asunto, "contenido": contenido}

    respuesta = requests.post(PREDICT_ENDPOINT, json=payload, timeout=TIMEOUT_S)
    respuesta.raise_for_status()  # levanta error si el status no es 2xx

    datos = respuesta.json()
    return datos["nivel_prioridad"]
