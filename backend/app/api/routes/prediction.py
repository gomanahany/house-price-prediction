from fastapi import APIRouter, Request

from app.schemas.prediction import PredictionRequest, PredictionResponse
from app.services.preprocessing import request_to_frame

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/predict", response_model=PredictionResponse)
def predict(payload: PredictionRequest, request: Request) -> PredictionResponse:
    frame = request_to_frame(payload)
    # Locations outside the exported top-location list deliberately become "other".
    allowed_locations = request.app.state.locations
    if payload.location not in allowed_locations:
        frame.loc[0, "location_grouped"] = "other"
    value = float(request.app.state.model.predict(frame)[0])
    return PredictionResponse(predicted_price=max(value, 0.0))
