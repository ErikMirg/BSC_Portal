from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg2://postgres:password@localhost:5432/BSCorporate"
    SECRET_KEY: str = "vPCU0X_7ugWS_Adc6sggJvaKOCH30PHvHasPf7exifE"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        extra = "ignore"

settings = Settings()