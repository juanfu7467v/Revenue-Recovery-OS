
from fastapi import APIRouter, Request, HTTPException
from src.database.firestore import db
from datetime import datetime, timedelta

router = APIRouter()

@router.post("/stripe")
async def stripe_webhook(request: Request):
    payload = await request.json()
    event_type = payload.get("type")

    if event_type == "invoice.payment_failed":
        invoice_data = payload["data"]["object"]
        customer_id = invoice_data.get("customer")
        invoice_id = invoice_data.get("id")
        amount = invoice_data.get("amount_due") / 100.0 # Stripe usa centavos
        currency = invoice_data.get("currency")

        # Registrar el pago fallido en Firestore
        recovery_log = {
            "invoice_id": invoice_id,
            "customer_id": customer_id,
            "amount": amount,
            "currency": currency,
            "status": "failed",
            "retry_count": 0,
            "created_at": datetime.now(),
            "next_retry_at": datetime.now() + timedelta(days=1) # Reintento inicial en 24h
        }
        db.collection("recovery_logs").document(invoice_id).set(recovery_log)
        
        # Aquí se dispararía la lógica de Smart Retries y Dunning
        return {"status": "success", "message": "Payment failure logged"}

    return {"status": "ignored"}
