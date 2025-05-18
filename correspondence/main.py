from .app import FastAPI
from .settings import settings

app = FastAPI.from_settings(settings)
