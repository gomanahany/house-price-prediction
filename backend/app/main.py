import json
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.prediction import router
from app.core.config import settings
from app.services.inference import load_model
from app.utils.logging_config import configure_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    app.state.model = load_model(settings.model_path)
    location_path = settings.model_path.with_name("locations.json")
    app.state.locations = set(json.loads(location_path.read_text(encoding="utf-8")))
    yield


app = FastAPI(title="House Price Prediction API", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=[settings.allowed_origin], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(router)
