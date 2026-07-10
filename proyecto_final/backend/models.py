from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    """Payload de entrada: los campos mínimos para predecir la prioridad."""

    asunto: str = Field(..., description="Asunto del ticket (Asunto_Ticket)")
    contenido: str = Field(..., description="Contenido del ticket (Contenido_Ticket)")


class PredictionResponse(BaseModel):
    """Respuesta con la prioridad predicha."""

    nivel_prioridad: str = Field(..., description="Baja, Media, Alta o Critica")
