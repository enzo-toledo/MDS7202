# Imagen base de Python
FROM python:3.12-slim

# Traemos el binario de uv desde su imagen oficial
COPY --from=ghcr.io/astral-sh/uv:0.11 /uv /uvx /bin/

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# El entorno virtual del proyecto vive en /app/.venv; lo dejamos en el PATH
ENV PATH="/app/.venv/bin:$PATH" \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# 1) Copiamos primero los archivos de uv para aprovechar la cache de capas de Docker
COPY pyproject.toml uv.lock ./

# 2) Instalamos exactamente las dependencias del lock
RUN uv sync --frozen --no-dev

# 3) Copiamos el resto del código (incluye modelo_final.pkl).
#    El .env queda fuera por el .dockerignore: la GOOGLE_API_KEY se inyecta
#    a nivel de contenedor (docker-compose), no dentro de la imagen.
COPY . .

EXPOSE 8000

# Entrypoint: levanta la API de FastAPI con uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
