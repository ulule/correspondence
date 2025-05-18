from .app import FastAPI
from .conf import settings

app = FastAPI.from_settings(settings)
