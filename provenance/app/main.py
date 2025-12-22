from fastapi import FastAPI, HTTPException
import mlflow
import os
import json
from datetime import datetime
from pydantic import BaseModel

app = FastAPI(title="Provenance")

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure MLflow
# In a real setup, MLflow would be a separate server service.
# Here we simulate using MLflow client to log/retrieve tracking data.
# We point to a local directory or the MinIO bucket if properly configured with S3 endpoint.
# For simplicity in this demo, we'll assume MLflow tracks to a local dir or sqlite
# and we expose an API to "audit" a score ID.

MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "file:///app/mlruns")
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

# Mock database of "Versions" for demo purposes
# Ideally we query the MLflow tracking server
provenance_log = {}

class ProvenanceRecord(BaseModel):
    score_id: int
    product_name: str
    calculation_date: str
    emissions_model_version: str # e.g. "v1.2-beta"
    dataset_hash: str # DVC hash of the factors dataset
    parameters: dict

@app.post("/provenance/log")
def log_provenance(record: ProvenanceRecord):
    # Log run to MLflow
    try:
        experiment = mlflow.get_experiment_by_name("LCA_Calculations")
        if not experiment:
            mlflow.create_experiment("LCA_Calculations")
        
        with mlflow.start_run(run_name=f"Score_{record.score_id}"):
            mlflow.log_param("score_id", record.score_id)
            mlflow.log_param("product", record.product_name)
            mlflow.log_param("model_version", record.emissions_model_version)
            mlflow.log_param("data_hash", record.dataset_hash)
            mlflow.log_dict(record.parameters, "calc_params.json")
            
            run_id = mlflow.active_run().info.run_id
            
        provenance_log[str(record.score_id)] = {
            "run_id": run_id,
            "record": record.dict(),
            "timestamp": datetime.now().isoformat()
        }
        return {"status": "logged", "run_id": run_id}
    except Exception as e:
        print(f"MLflow Log Error: {e}")
        # Fallback to local dict for demo if MLflow setup fails
        provenance_log[str(record.score_id)] = {
            "error": str(e),
            "record": record.dict()
        }
        return {"status": "fallback_logged"}

@app.get("/provenance/{score_id}")
def get_provenance(score_id: str):
    if score_id not in provenance_log:
        raise HTTPException(status_code=404, detail="Provenance data not found for this score")
    
    return provenance_log[score_id]
