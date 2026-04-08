
from fastapi import APIRouter, Depends
from src.database.firestore import db
from src.api.v1.schemas import DashboardMetrics

router = APIRouter()

@router.get("/metrics", response_model=DashboardMetrics)
async def get_dashboard_metrics(user_id: str):
    # Obtener logs de recuperación del usuario de Firestore
    recovery_logs = db.collection("recovery_logs").where("user_id", "==", user_id).stream()
    
    recovered_amount = 0.0
    total_collection_days = 0
    accounts_at_risk = 0
    count_recovered = 0
    
    for log in recovery_logs:
        data = log.to_dict()
        if data.get("status") == "recovered":
            recovered_amount += data.get("amount", 0.0)
            count_recovered += 1
            # Lógica simple de reducción en días de cobro
            total_collection_days += data.get("collection_days", 0)
        elif data.get("status") in ["failed", "failed_retry"]:
            accounts_at_risk += 1
            
    reduction_in_collection_days = total_collection_days / count_recovered if count_recovered > 0 else 0.0
    
    return {
        "recovered_amount": recovered_amount,
        "reduction_in_collection_days": reduction_in_collection_days,
        "accounts_at_risk": accounts_at_risk
    }
