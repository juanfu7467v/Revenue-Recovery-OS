import firebase_admin
from firebase_admin import credentials, firestore
import os

def initialize_firebase():
    if not firebase_admin._apps:
        # Intentar cargar desde variables de entorno individuales (Fly.io)
        firebase_config = {
            "type": os.getenv("FIREBASE_TYPE"),
            "project_id": os.getenv("FIREBASE_PROJECT_ID"),
            "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
            "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace("\\n", "\n") if os.getenv("FIREBASE_PRIVATE_KEY") else None,
            "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
            "client_id": os.getenv("FIREBASE_CLIENT_ID"),
            "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
            "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
            "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_X509_CERT_URL"),
            "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL"),
            "universe_domain": os.getenv("FIREBASE_UNIVERSE_DOMAIN")
        }
        
        # Verificar si las variables críticas están presentes
        if all([firebase_config["project_id"], firebase_config["private_key"], firebase_config["client_email"]]):
            cred = credentials.Certificate(firebase_config)
        else:
            # Fallback a archivo local si no hay variables de entorno (Desarrollo local)
            cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "./firebase-adminsdk.json")
            if os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
            else:
                raise ValueError("No Firebase credentials found in environment or local file.")
                
        firebase_admin.initialize_app(cred)
    return firestore.client()

db = initialize_firebase()
