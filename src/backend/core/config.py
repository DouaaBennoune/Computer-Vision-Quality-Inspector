from pydantic_settings import BaseSettings
import logging

class Settings(BaseSettings):
    PROJECT_NAME: str='Computer Quality Inspector'
    VERSION: str="1.0.0"
    DESCRIPTION: str="Cv API"
    API_V1_STR: str = "/api/v1"
    CORS_ORIGINS : list[str]= ["*"]
    LOG_LEVEL : int = logging.INFO

settings = Settings()
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format=("%(asctime)s - %(levelname)s - %(message)s")

)
logger= logging.getLogger(settings.PROJECT_NAME)