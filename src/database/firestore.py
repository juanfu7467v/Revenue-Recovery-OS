import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

def initialize_firebase():
    if not firebase_admin._apps:
        # Obtener variables de entorno
        fb_type = os.getenv("FIREBASE_TYPE", "service_account")
        project_id = os.getenv("FIREBASE_PROJECT_ID")
        private_key_id = os.getenv("FIREBASE_PRIVATE_KEY_ID")
        private_key = os.getenv("FIREBASE_PRIVATE_KEY")
        client_email = os.getenv("FIREBASE_CLIENT_EMAIL")
        client_id = os.getenv("FIREBASE_CLIENT_ID")
        auth_uri = os.getenv("FIREBASE_AUTH_URI", "https://accounts.google.com/o/oauth2/auth")
        token_uri = os.getenv("FIREBASE_TOKEN_URI", "https://oauth2.googleapis.com/token")
        auth_provider_cert = os.getenv("FIREBASE_AUTH_PROVIDER_X509_CERT_URL", "https://www.googleapis.com/oauth2/v1/certs")
        client_cert = os.getenv("FIREBASE_CLIENT_X509_CERT_URL")
        universe_domain = os.getenv("FIREBASE_UNIVERSE_DOMAIN", "googleapis.com")

        # Limpieza de la clave privada (manejo de saltos de línea)
        if private_key:
            # Si la clave viene con comillas literales al inicio/fin, las quitamos
            private_key = private_key.strip('"').strip("'")
            # Reemplazamos los \n literales por saltos de línea reales
            private_key = private_key.replace("\\n", "\n")

        # Construir el diccionario de configuración
        firebase_config = {
            "type": fb_type,
            "project_id": project_id,
            "private_key_id": private_key_id,
            "private_key": private_key,
            "client_email": client_email,
            "client_id": client_id,
            "auth_uri": auth_uri,
            "token_uri": token_uri,
            "auth_provider_x509_cert_url": auth_provider_cert,
            "client_x509_cert_url": client_cert,
            "universe_domain": universe_domain
        }
        
        # Depuración (sin mostrar la clave privada completa por seguridad)
        print(f"DEBUG: Initializing Firebase for project: {project_id}")
        print(f"DEBUG: Firebase Type: {fb_type}")
        print(f"DEBUG: Client Email: {client_email}")
        
        # Verificar si las variables críticas están presentes
        critical_fields = ["project_id", "private_key", "client_email"]
        missing_fields = [field for field in critical_fields if not firebase_config[field]]
        
        if not missing_fields:
            try:
                cred = credentials.Certificate(firebase_config)
                firebase_admin.initialize_app(cred)
                print("SUCCESS: Firebase initialized successfully.")
            except Exception as e:
                print(f"ERROR: Failed to initialize Firebase with provided config: {e}")
                return None
        else:
            # Fallback a archivo local si no hay variables de entorno (Desarrollo local)
            print(f"WARNING: Missing environment variables: {', '.join(missing_fields)}")
            cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "./firebase-adminsdk.json")
            if os.path.exists(cred_path):
                try:
                    cred = credentials.Certificate(cred_path)
                    firebase_admin.initialize_app(cred)
                    print(f"SUCCESS: Firebase initialized using local file: {cred_path}")
                except Exception as e:
                    print(f"ERROR: Failed to initialize Firebase with local file: {e}")
                    return None
            else:
                print("CRITICAL: No Firebase credentials found in environment or local file.")
                return None
                
    try:
        return firestore.client()
    except Exception as e:
        print(f"ERROR: Could not get Firestore client: {e}")
        return None

# Inicialización global
db = initialize_firebase()
