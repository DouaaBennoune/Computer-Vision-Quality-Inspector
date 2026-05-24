from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.core.config import settings
from backend.api import endpoints
import uvicorn
import os

def create_app() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.DESCRIPTION,
        version=settings.VERSION
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
        )
    os.makedirs("static", exist_ok=True)

    application.mount("/static", StaticFiles(directory="static"), name="static")
    application.include_router(endpoints.router,prefix="/api/v1",tags=["Prediction"])
    @application.get("/health")
    async def health_check():
        return{"status":"healthy","version":settings.VERSION}

    @application.get("/",include_in_schema=False)
    async def root():
        """Redirect root to docs"""
        return RedirectResponse(url="/docs")
    return application

app=create_app()

if __name__=="__main__":
    uvicorn.run("app.main:app",host="0.0.0.0",port=8000,reload=True)
