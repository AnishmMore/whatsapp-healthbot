import uvicorn
from fastapi import FastAPI
from config import Settings, configure_logging
from api.router import router

settings = Settings()

def create_app() -> FastAPI:
    app = FastAPI()
    configure_logging()
    app.include_router(router)

    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run(app, port=8000)
