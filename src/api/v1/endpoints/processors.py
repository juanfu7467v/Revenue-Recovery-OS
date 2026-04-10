from fastapi import APIRouter, Request, HTTPException, Header, BackgroundTasks
from src.database.firestore import db
from src.config import settings
from src.services.smart_retries import SmartRetries
from src.services.dunning import DunningService
from datetime import datetime, timedelta
import json

router = APIRouter()

async def process_generic_recovery(processor_name: str, event_data: dict, org_id: str = "default_org"):
    """
    Lógica genérica de recuperación para cualquier procesador de pago.
    """
    customer_id = event_data.get("customer_id")
    invoice_id = event_data.get("invoice_id")
    amount = event_data.get("amount")
    currency = event_data.get("currency", "USD")
    
    # Guardar log de recuperación
    if db:
        try:
            recovery_log = {
                "processor": processor_name,
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
            db.collection("recovery_logs").document(f"{processor_name}_{invoice_id}").set(recovery_log)
        except Exception as e:
            print(f"Error saving to Firestore ({processor_name}): {e}")

    # 1. Iniciar Smart Retries
    retrier = SmartRetries(invoice_id)
    await retrier.execute_retry()
    
    # 2. Disparar Dunning Multicanal
    dunning = DunningService(org_id)
    await dunning.trigger_dunning(customer_id, invoice_id, amount)

@router.post("/adyen")
async def adyen_webhook(request: Request, background_tasks: BackgroundTasks):
    """Webhook para Adyen (Empresas Grandes)"""
    payload = await request.json()
    # Lógica de validación de Adyen aquí
    
    # Ejemplo de extracción de datos (simplificado)
    notification_items = payload.get("notificationItems", [])
    for item in notification_items:
        details = item.get("NotificationRequestItem", {})
        if details.get("eventCode") == "AUTHORISATION" and details.get("success") == "false":
            event_data = {
                "customer_id": details.get("pspReference"),
                "invoice_id": details.get("merchantReference"),
                "amount": float(details.get("amount", {}).get("value", 0)) / 100,
                "currency": details.get("amount", {}).get("currency")
            }
            background_tasks.add_task(process_generic_recovery, "adyen", event_data)
            
    return {"status": "accepted"}

@router.post("/paypal-braintree")
async def paypal_braintree_webhook(request: Request, background_tasks: BackgroundTasks):
    """Webhook para PayPal / Braintree (E-commerce)"""
    # Braintree suele enviar datos en formato form-url-encoded para webhooks
    # pero aquí simulamos JSON para consistencia
    payload = await request.json()
    
    # Lógica de extracción para Braintree
    event_kind = payload.get("kind")
    if event_kind == "subscription_charge_unsuccessful":
        subscription = payload.get("subscription", {})
        event_data = {
            "customer_id": subscription.get("customer_id"),
            "invoice_id": subscription.get("id"),
            "amount": float(subscription.get("price", 0)),
            "currency": subscription.get("currency_iso_code")
        }
        background_tasks.add_task(process_generic_recovery, "paypal_braintree", event_data)
        
    return {"status": "ok"}

@router.post("/checkout")
async def checkout_webhook(request: Request, background_tasks: BackgroundTasks):
    """Webhook para Checkout.com (Europa y Asia)"""
    payload = await request.json()
    
    event_type = payload.get("type")
    if event_type == "payment_declined":
        data = payload.get("data", {})
        event_data = {
            "customer_id": data.get("customer", {}).get("id"),
            "invoice_id": data.get("reference"),
            "amount": float(data.get("amount", 0)) / 100,
            "currency": data.get("currency")
        }
        background_tasks.add_task(process_generic_recovery, "checkout", event_data)
        
    return {"status": "ok"}

@router.post("/mercadopago")
async def mercadopago_webhook(request: Request, background_tasks: BackgroundTasks):
    """Webhook para Mercado Pago (Latinoamérica)"""
    payload = await request.json()
    
    # Mercado Pago envía notificaciones de tipo 'payment' o 'subscription_preapproval'
    action = payload.get("action")
    if action == "payment.created" or action == "payment.updated":
        # En una implementación real, se consultaría la API de MP con el ID recibido
        # para verificar el estado 'rejected'
        payment_id = payload.get("data", {}).get("id")
        # Simulación de datos extraídos
        event_data = {
            "customer_id": "mp_cust_123",
            "invoice_id": f"mp_pay_{payment_id}",
            "amount": 0.0, # Se obtendría de la API
            "currency": "ARS"
        }
        background_tasks.add_task(process_generic_recovery, "mercadopago", event_data)
        
    return {"status": "ok"}

@router.post("/payu")
async def payu_webhook(request: Request, background_tasks: BackgroundTasks):
    """Webhook para PayU (Latinoamérica)"""
    payload = await request.json()
    
    state = payload.get("state_pol")
    if state == "6": # DECLINED en PayU
        event_data = {
            "customer_id": payload.get("payer_id"),
            "invoice_id": payload.get("reference_sale"),
            "amount": float(payload.get("value", 0)),
            "currency": payload.get("currency")
        }
        background_tasks.add_task(process_generic_recovery, "payu", event_data)
        
    return {"status": "ok"}

@router.post("/kushki-niubiz")
async def kushki_niubiz_webhook(request: Request, background_tasks: BackgroundTasks):
    """Webhook para Kushki / Niubiz (Perú y Países Andinos)"""
    payload = await request.json()
    
    # Kushki usa 'transaction_status'
    status = payload.get("transaction_status")
    if status == "DECLINED":
        event_data = {
            "customer_id": payload.get("customer_id"),
            "invoice_id": payload.get("ticket_number"),
            "amount": float(payload.get("amount", 0)),
            "currency": payload.get("currency")
        }
        background_tasks.add_task(process_generic_recovery, "kushki_niubiz", event_data)
        
    return {"status": "ok"}
