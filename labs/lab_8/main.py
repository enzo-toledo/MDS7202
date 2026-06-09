import pickle

import pandas as pd
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

# Cargar el mejor modelo de la parte anterior:
with open("models/best_model.pkl", "rb") as f:
    model = pickle.load(f)

app = FastAPI(title="FastAPI Potabilidad del Agua")


# Esquema del body (mismas columnas y orden que el dataset de entrenamiento!):
class WaterSample(BaseModel):
    ph: float
    Hardness: float
    Solids: float
    Chloramines: float
    Sulfate: float
    Conductivity: float
    Organic_carbon: float
    Trihalomethanes: float
    Turbidity: float


@app.get("/")
def home():
    return {
        "modelo": "XGBoost optimizado con Optuna + MLflow",
        "problema": "Clasificacion binaria de potabilidad del agua a partir de 9 mediciones.",
        "entrada": "JSON con: ph, Hardness, Solids, Chloramines, Sulfate, "
        "Conductivity, Organic_carbon, Trihalomethanes, Turbidity",
        "salida": "JSON {'potabilidad': 0 o 1}, donde 1 = agua potable y 0 = no potable.",
    }


@app.post("/potabilidad/")
def predict_potabilidad(sample: WaterSample):
    # Convertir el body a DataFrame respetando los nombres de columnas del entrenamiento:
    X = pd.DataFrame([sample.model_dump()])
    pred = model.predict(X)
    return {"potabilidad": int(pred[0])}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
