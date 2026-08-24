import pandas as pd

from app.schemas.prediction import PredictionRequest


def request_to_frame(request: PredictionRequest) -> pd.DataFrame:
    """Map an API request to exactly the column names used while training."""
    return pd.DataFrame([{
        "carpet_area_sqft": request.carpet_area_sqft,
        "floor_num": request.floor_num,
        "bathroom": request.bathroom,
        "balcony": request.balcony,
        "car_parking": request.car_parking,
        "location_grouped": request.location,
        "Furnishing": request.furnishing,
        "Transaction": request.transaction,
        "Ownership": request.ownership,
        "facing": request.facing,
    }])
