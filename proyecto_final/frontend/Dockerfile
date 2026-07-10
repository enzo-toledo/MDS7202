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

# 1) Copiamos primero los archivos de uv para aprovechar la cache de capas
COPY pyproject.toml uv.lock ./

# 2) Instalamos exactamente las dependencias del lock
RUN uv sync --frozen --no-dev

# 3) Copiamos el resto del código (app.py, services.py)
COPY . .

EXPOSE 7860

# Entrypoint: levanta la app de Gradio
CMD ["python", "app.py"]
