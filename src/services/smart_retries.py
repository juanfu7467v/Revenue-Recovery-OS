from datetime import datetime, timedelta
from src.database.firestore import db

class SmartRetries:
    def __init__(self, invoice_id: str):
        self.invoice_id = invoice_id
        self.invoice_ref = db.collection("recovery_logs").document(invoice_id) if db else None

    def calculate_next_retry(self, current_retry_count: int) -> datetime:
        # Lógica de reintento exponencial o basada en eventos históricos
        # Por ahora: 1 día, 3 días, 7 días, 14 días
        retry_intervals = [1, 3, 7, 14]
        if current_retry_count < len(retry_intervals):
            days_to_wait = retry_intervals[current_retry_count]
        else:
            days_to_wait = 30 # Último reintento al mes
        return datetime.now() + timedelta(days=days_to_wait)

    async def execute_retry(self):
        if not self.invoice_ref:
            print("SmartRetries: Database connection not available.")
            return {"status": "error", "message": "Database connection not available"}
        
        try:
            invoice_doc = self.invoice_ref.get()
            if not invoice_doc.exists:
                return {"status": "error", "message": "Invoice not found"}
            
            data = invoice_doc.to_dict()
            current_retry_count = data.get("retry_count", 0)
            
            # Aquí se integraría con el procesador de pagos (Stripe, Adyen) para reintentar el cobro
            # Supongamos que falla de nuevo:
            next_retry_at = self.calculate_next_retry(current_retry_count)
            self.invoice_ref.update({
                "retry_count": current_retry_count + 1,
                "last_retry_at": datetime.now(),
                "next_retry_at": next_retry_at,
                "status": "failed_retry"
            })
            return {"status": "retry_scheduled", "next_retry_at": next_retry_at}
        except Exception as e:
            print(f"SmartRetries: Error executing retry: {e}")
            return {"status": "error", "message": str(e)}
