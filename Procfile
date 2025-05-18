web: uvicorn correspondence.main:app --host=0.0.0.0 --port=${PORT:-5000} --log-config uvicorn_disable_logging.json
worker: taskiq worker correspondence.broker:broker
