from fastapi import APIRouter, Depends, HTTPException
from src.database.firestore import db
from src.api.v1.schemas import DashboardMetrics

router = APIRouter()

from src.utils.auth import get_current_user

@router.get("/metrics", response_model=DashboardMetrics)
async def get_dashboard_metrics(current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    if not db:
        raise HTTPException(status_code=503, detail="Database connection not available. Please check Firebase configuration.")
    
    try:
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
        
        # Nuevas métricas
        monthly_recovered = recovered_amount # Simplificación para el demo
        total_attempts = count_recovered + accounts_at_risk
        recovery_rate = (count_recovered / total_attempts * 100) if total_attempts > 0 else 0.0
        
        message_summary = f"Este mes has recuperado ${monthly_recovered:,.2f} USD que dabas por perdidos"
        
        return {
            "recovered_amount": recovered_amount,
            "reduction_in_collection_days": reduction_in_collection_days,
            "accounts_at_risk": accounts_at_risk,
            "monthly_recovered": monthly_recovered,
            "recovery_rate": recovery_rate,
            "active_recovery_campaigns": accounts_at_risk,
            "message_summary": message_summary
        }
    except Exception as e:
        print(f"Error fetching metrics from Firestore: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving dashboard metrics.")
