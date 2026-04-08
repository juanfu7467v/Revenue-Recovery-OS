
from src.database.firestore import db

class RecoveryScoring:
    def __init__(self, invoice_id: str):
        self.invoice_id = invoice_id
        self.invoice_ref = db.collection("recovery_logs").document(invoice_id)

    def calculate_score(self, amount: float, retry_count: int, last_payment_status: str) -> float:
        # Lógica de scoring: 0.0 a 1.0 (probabilidad de pago)
        # Por ahora: 
        #   - Si el monto es alto, el score es más alto (prioridad)
        #   - Si el retry_count es alto, el score baja (menos probable)
        #   - Si el último pago fue exitoso, el score es más alto
        
        base_score = 0.5
        
        if amount > 1000:
            base_score += 0.2
        elif amount < 50:
            base_score -= 0.1
        
        if retry_count > 3:
            base_score -= 0.3
        
        if last_payment_status == "success":
            base_score += 0.2
        
        # Mantener el score dentro del rango 0.0 a 1.0
        return max(0.0, min(1.0, base_score))

    async def update_score(self, amount: float, retry_count: int, last_payment_status: str):
        score = self.calculate_score(amount, retry_count, last_payment_status)
        self.invoice_ref.update({
            "recovery_score": score,
            "priority": "high" if score > 0.7 else "medium" if score > 0.4 else "low"
        })
        return score
