
from src.database.firestore import db
from src.utils.encryption import encrypt_token, decrypt_token
from datetime import datetime

class VaultService:
    @staticmethod
    def store_api_key(org_id: str, processor: str, api_key: str):
        encrypted_key = encrypt_token(api_key)
        vault_ref = db.collection("vault").document(f"{org_id}_{processor}")
        vault_ref.set({
            "org_id": org_id,
            "processor": processor,
            "api_key_encrypted": encrypted_key,
            "updated_at": datetime.utcnow()
        })
        return True

    @staticmethod
    def get_api_key(org_id: str, processor: str) -> str:
        vault_doc = db.collection("vault").document(f"{org_id}_{processor}").get()
        if not vault_doc.exists:
            return None
        
        data = vault_doc.to_dict()
        return decrypt_token(data["api_key_encrypted"])
