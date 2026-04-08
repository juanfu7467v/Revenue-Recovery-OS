
import os
from src.database.firestore import db

class DunningService:
    def __init__(self, user_id: str):
        self.user_id = user_id

    async def send_email(self, customer_email: str, invoice_id: str, amount: float):
        # Lógica de envío de email (e.g., SendGrid)
        print(f"Sending Dunning Email to {customer_email} for invoice {invoice_id}")
        return {"status": "email_sent"}

    async def send_whatsapp(self, customer_phone: str, invoice_id: str, amount: float):
        # Lógica de envío de WhatsApp (e.g., Twilio)
        print(f"Sending Dunning WhatsApp to {customer_phone} for invoice {invoice_id}")
        return {"status": "whatsapp_sent"}

    async def send_sms(self, customer_phone: str, invoice_id: str, amount: float):
        # Lógica de envío de SMS (e.g., Twilio)
        print(f"Sending Dunning SMS to {customer_phone} for invoice {invoice_id}")
        return {"status": "sms_sent"}

    async def trigger_dunning(self, customer_id: str, invoice_id: str, amount: float):
        # Lógica de decisión de canal basada en configuración del usuario
        # Por ahora, simplemente enviamos un email por defecto
        # En una versión más avanzada, esto dependería del scoring de recuperación
        customer_doc = db.collection("customers").document(customer_id).get()
        if not customer_doc.exists:
            return {"status": "error", "message": "Customer not found"}
        
        customer_data = customer_doc.to_dict()
        email = customer_data.get("email")
        
        if email:
            await self.send_email(email, invoice_id, amount)
        
        return {"status": "dunning_triggered"}
