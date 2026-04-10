from fastapi import APIRouter, Request, HTTPException, Header, BackgroundTasks
from src.database.firestore import db
from src.config import settings
from src.services.smart_retries import SmartRetries
from src.services.dunning import DunningService
import stripe
from datetime import datetime, timedelta
import json

router = APIRouter()

async def process_recovery_logic(event: dict):
    event_type = event.get("type")
    if event_type == "invoice.payment_failed":
        invoice_data = event["data"]["object"]
        customer_id = invoice_data.get("customer")
        invoice_id = invoice_data.get("id")
        amount = invoice_data.get("amount_due") / 100.0
        
        org_id = invoice_data.get("metadata", {}).get("org_id", "default_org")
        
        # 1. Iniciar Smart Retries
        retrier = SmartRetries(invoice_id)
        await retrier.execute_retry()
        
        # 2. Disparar Dunning Multicanal
        dunning = DunningService(org_id)
        await dunning.trigger_dunning(customer_id, invoice_id, amount)

@router.post("/stripe")
async def stripe_webhook(request: Request, background_tasks: BackgroundTasks, stripe_signature: str = Header(None)):
    payload = await request.body()
    
    # En producción, validar la firma del webhook
    if settings.STRIPE_WEBHOOK_SECRET:
        try:
            event = stripe.Webhook.construct_event(
                payload, stripe_signature, settings.STRIPE_WEBHOOK_SECRET
            )
        except (ValueError, stripe.error.SignatureVerificationError) as e:
            raise HTTPException(status_code=400, detail=str(e))
    else:
        # Modo desarrollo: procesar sin validar firma si no hay secreto
        try:
            event = json.loads(payload)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid payload")

    event_type = event.get("type")
    
    # Guardar el evento para auditoría en recovery_events si db está disponible
    if db:
        try:
            event_id = event.get("id", f"evt_{datetime.utcnow().timestamp()}")
            db.collection("recovery_events").document(event_id).set({
                "event_type": event_type,
                "payload": event,
                "received_at": datetime.utcnow()
            })
        except Exception as e:
            print(f"Error saving to Firestore (recovery_events): {e}")

    if event_type == "invoice.payment_failed":
        invoice_data = event["data"]["object"]
        customer_id = invoice_data.get("customer")
        invoice_id = invoice_data.get("id")
        amount = invoice_data.get("amount_due") / 100.0
        currency = invoice_data.get("currency")
        
        org_id = invoice_data.get("metadata", {}).get("org_id", "default_org")

        if db:
            try:
                recovery_log = {
                    "org_id": org_id,
                    "invoice_id": invoice_id,
                    "customer_id": customer_id,
                    "amount": amount,
                    "currency": currency,
                    "status": "failed",
                    "retry_count": 0,
                    "created_at": datetime.utcnow(),
                    "next_retry_at": datetime.utcnow() + timedelta(days=1)
                }
                db.collection("recovery_logs").document(invoice_id).set(recovery_log)
            except Exception as e:
                print(f"Error saving to Firestore (recovery_logs): {e}")
        
        # Procesar lógica pesada en segundo plano
        background_tasks.add_task(process_recovery_logic, event)
        
        return {"status": "success", "message": "Payment failure logged, recovery logic queued"}

    elif event_type == "customer.subscription.updated":
        # Lógica de Pre-Dunning: Detectar si el método de pago está por vencer
        obj = event["data"]["object"]
        org_id = obj.get("metadata", {}).get("org_id", "default_org")
        
        # Simulamos detección de tarjeta por vencer (basado en lógica de negocio)
        # En una implementación real, extraeríamos datos del PaymentMethod asociado
        customer_id = obj.get("customer")
        customer_email = "cliente@ejemplo.com" # Placeholder
        card_last4 = "4242" # Placeholder
        expiry_date = "12/26" # Placeholder
        
        dunning = DunningService(org_id)
        background_tasks.add_task(dunning.send_pre_dunning_notification, customer_email, card_last4, expiry_date)
        
        return {"status": "success", "message": "Pre-Dunning notification queued"}

    return {"status": "success", "message": "Event received"}
