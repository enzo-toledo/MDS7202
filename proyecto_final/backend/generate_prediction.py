"""
El modelo final (MLP + Embeddings) solo usa los 1024 embeddings del texto,
por lo que los campos mínimos son el asunto y el contenido del ticket.
"""

import pickle
import time

import pandas as pd
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Con esto cargamos la GOOGLE_API_KEY del .env:
load_dotenv()

# Parametros:
EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIM = 1024
EMBEDDING_COLS = [f"embedding_dim_{i}" for i in range(1, EMBEDDING_DIM + 1)]
MODEL_PATH = "./modelo_final.pkl"


def _load_model():
    with open(MODEL_PATH, "rb") as f:
        return pickle.load(f)


def _build_text(asunto: str, contenido: str) -> str:
    """
    Construye el texto tal y como se hizo al generar los embeddings.
    """
    return f"Asunto_Ticket: {asunto}\nContenido_Ticket: {contenido}\n"


def _embed_text(texto: str) -> list[float]:
    """
    Vectoriza el texto con gemini-embedding-001 a 1024 dimensiones.
    """
    embeddings = GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL,
        output_dimensionality=EMBEDDING_DIM,
    )
    return embeddings.embed_query(texto)


def generate_prediction(asunto: str, contenido: str) -> str:
    """
    Predice el Nivel_Prioridad de un ticket a partir del asunto y el contenido.
    """

    # Construir el texto y vectorizarlo igual que en el entrenamiento:
    texto = _build_text(asunto, contenido)
    vector = _embed_text(texto)

    # Armar el DataFrame con las columnas nombradas que el pipeline espera:
    X = pd.DataFrame([vector], columns=EMBEDDING_COLS)

    # Cargar el pipeline y predecir:
    modelo = _load_model()
    pred = modelo.predict(X)[0]

    return str(pred)


if __name__ == "__main__":
    # Ejemplo:
    asunto_ej = "Cobro desconocido en mi tarjeta de crédito"
    contenido_ej = (
        "Hola, revisé mi cuenta y aparece un cobro que no conozco. "
        "Necesito que lo revisen con urgencia porque es mucho dinero."
    )
    start_time = time.time()
    resultado = generate_prediction(asunto_ej, contenido_ej)
    end_time = time.time()
    print(f"Asunto:    {asunto_ej}")
    print(f"Contenido: {contenido_ej}")
    print(f"Predicción Nivel_Prioridad: {resultado}")
    print(f"Tiempo de inferencia: {end_time - start_time:.2f} segundos")
