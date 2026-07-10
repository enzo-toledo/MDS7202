import uvicorn
from fastapi import FastAPI, HTTPException
from generate_prediction import generate_prediction
from models import PredictionRequest, PredictionResponse

app = FastAPI(
    title="ChaucherApp",
    description="Predice el Nivel_Prioridad de un ticket de soporte a partir de su asunto y contenido.",
    version="1.0.0",
)


@app.get("/")
def home():
    return {
        "modelo": "MLP + Embeddings (gemini-embedding-001, 1024 dims)",
        "problema": "Clasificación multiclase de prioridad de tickets de soporte.",
        "entrada": "JSON con: asunto, contenido",
        "salida": "JSON {'nivel_prioridad': 'Baja', 'Media', 'Alta' o 'Critica'}",
    }


@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest) -> PredictionResponse:
    try:
        pred = generate_prediction(
            asunto=request.asunto,
            contenido=request.contenido,
        )
        return PredictionResponse(nivel_prioridad=pred)
    except Exception as e:
        # Cualquier fallo (API de embeddings caída, modelo no carga, etc.)
        raise HTTPException(status_code=500, detail=f"Error al generar la predicción: {e}")  # noqa: B904


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
