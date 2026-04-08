
import os

class Settings:
    PROJECT_NAME: str = "Cashflow Recovery API"
    PROJECT_VERSION: str = "0.1.0"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    FIREBASE_CREDENTIALS_PATH: str = os.getenv("FIREBASE_CREDENTIALS_PATH", "./firebase-adminsdk.json")
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY", "a_super_secret_key_for_encryption") # ¡Cambiar en producción!

settings = Settings()
