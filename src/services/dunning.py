import os
from src.database.firestore import db

class DunningService:
    def __init__(self, user_id: str):
        self.user_id = user_id

    async def _get_branding(self):
        if not db:
            return {}
        org_doc = db.collection("empresas").document(self.user_id).get()
        if org_doc.exists:
            return org_doc.to_dict().get("branding", {})
        return {}

    async def send_email(self, customer_email: str, invoice_id: str, amount: float):
        branding = await self._get_branding()
        company_name = branding.get("company_name", "Nuestra Empresa")
        tone = branding.get("tone", "professional")
        
        # Lógica de personalización por tono
        templates = {
            "professional": f"Estimado cliente, le informamos que el pago de su factura {invoice_id} por ${amount} ha fallado.",
            "friendly": f"¡Hola! Tuvimos un pequeño problema con el pago de tu factura {invoice_id}. No te preocupes, suele ser algo rápido de solucionar.",
            "urgent": f"ATENCIÓN: El pago de su factura {invoice_id} ha fallado. Por favor actualice su método de pago inmediatamente para evitar la suspensión del servicio."
        }
        
        message = templates.get(tone, templates["professional"])
        
        print(f"[{company_name}] Sending Dunning Email to {customer_email}: {message}")
        return {"status": "email_sent", "branding_applied": True}

    async def send_pre_dunning_notification(self, customer_email: str, card_last4: str, expiry_date: str):
        branding = await self._get_branding()
        company_name = branding.get("company_name", "Nuestra Empresa")
        
        message = f"Tu tarjeta terminada en {card_last4} vence pronto ({expiry_date}). Actualízala aquí para evitar interrupciones en el servicio."
        
        print(f"[{company_name}] Sending Pre-Dunning Notification to {customer_email}: {message}")
        return {"status": "pre_dunning_sent"}

    async def send_whatsapp(self, customer_phone: str, invoice_id: str, amount: float):
        # Lógica de envío de WhatsApp (e.g., Twilio)
        print(f"Sending Dunning WhatsApp to {customer_phone} for invoice {invoice_id}")
        return {"status": "whatsapp_sent"}

    async def send_sms(self, customer_phone: str, invoice_id: str, amount: float):
        # Lógica de envío de SMS (e.g., Twilio)
        print(f"Sending Dunning SMS to {customer_phone} for invoice {invoice_id}")
        return {"status": "sms_sent"}

    async def trigger_dunning(self, customer_id: str, invoice_id: str, amount: float):
        if not db:
            print("DunningService: Database connection not available.")
            return {"status": "error", "message": "Database connection not available"}
        
        try:
            customer_doc = db.collection("customers").document(customer_id).get()
            if not customer_doc.exists:
                return {"status": "error", "message": "Customer not found"}
            
            customer_data = customer_doc.to_dict()
            email = customer_data.get("email")
            
            if email:
                await self.send_email(email, invoice_id, amount)
            
            return {"status": "dunning_triggered"}
        except Exception as e:
            print(f"DunningService: Error triggering dunning: {e}")
            return {"status": "error", "message": str(e)}
