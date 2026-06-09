# Usa una imagen base de Python
FROM python:3.11-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia e instala las dependencias
COPY requirements_docker.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de la aplicación
COPY main.py .
COPY models/ ./models/

# Volumen para persistencia de datos
VOLUME ["/app/data"]

# Expone el puerto de la API
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
