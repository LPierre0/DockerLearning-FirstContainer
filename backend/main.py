from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import asyncio
import json
import random
import math
from datetime import datetime
from typing import Generator

app = FastAPI(title="Data Science Dashboard API")

origins = [
    "http://localhost",
    "http://localhost:7958",
    "http://localhost:5173",
    "http://localhost:8000",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ═══════════════════════════════════════════════════════════════
# 📊 PROFILE & SKILLS DATA
# ═══════════════════════════════════════════════════════════════

PROFILE = {
    "name": "Pierre Lafage",
    "title": "Data Scientist & Data Engineer",
    "bio": "Passionné par la data science et le machine learning, je développe des solutions innovantes pour extraire de la valeur des données.",
    "github": "https://github.com/LPierre0",
    "linkedin": "https://www.linkedin.com/in/pierre-lafage-31b520251/",
    "specialties": ["Machine Learning", "Data Engineering", "MLOps", "Real-time Analytics"]
}

SKILLS = [
    {"name": "Python", "level": 95, "category": "Languages", "icon": "🐍"},
    {"name": "SQL", "level": 90, "category": "Languages", "icon": "🗃️"},
    {"name": "Pandas", "level": 92, "category": "Data", "icon": "🐼"},
    {"name": "Scikit-learn", "level": 88, "category": "ML", "icon": "🤖"},
    {"name": "TensorFlow", "level": 75, "category": "ML", "icon": "🧠"},
    {"name": "PyTorch", "level": 70, "category": "ML", "icon": "🔥"},
    {"name": "Apache Spark", "level": 80, "category": "Big Data", "icon": "⚡"},
    {"name": "Docker", "level": 85, "category": "DevOps", "icon": "🐳"},
    {"name": "Kubernetes", "level": 65, "category": "DevOps", "icon": "☸️"},
    {"name": "Airflow", "level": 78, "category": "Orchestration", "icon": "🌬️"},
    {"name": "FastAPI", "level": 88, "category": "Backend", "icon": "⚡"},
    {"name": "PostgreSQL", "level": 85, "category": "Databases", "icon": "🐘"},
    {"name": "MongoDB", "level": 72, "category": "Databases", "icon": "🍃"},
    {"name": "Redis", "level": 70, "category": "Databases", "icon": "🔴"},
    {"name": "Git", "level": 90, "category": "Tools", "icon": "📦"},
]

# ═══════════════════════════════════════════════════════════════
# 🔬 MACHINE LEARNING SIMULATION
# ═══════════════════════════════════════════════════════════════

class MLSimulator:
    """Simulates ML model training and predictions"""
    
    @staticmethod
    def generate_training_metrics(epoch: int, total_epochs: int) -> dict:
        """Generate realistic training metrics"""
        progress = epoch / total_epochs
        # Simule une courbe d'apprentissage réaliste
        base_loss = 2.5 * math.exp(-3 * progress) + 0.1 + random.uniform(-0.05, 0.05)
        accuracy = min(0.98, 0.5 + 0.48 * (1 - math.exp(-4 * progress)) + random.uniform(-0.02, 0.02))
        val_loss = base_loss * (1 + 0.1 * random.random())
        val_accuracy = accuracy * (0.95 + 0.05 * random.random())
        
        return {
            "epoch": epoch,
            "loss": round(base_loss, 4),
            "accuracy": round(accuracy, 4),
            "val_loss": round(val_loss, 4),
            "val_accuracy": round(val_accuracy, 4),
            "learning_rate": round(0.001 * (0.95 ** (epoch // 10)), 6),
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def predict_regression(x: float) -> dict:
        """Simulate a regression prediction with uncertainty"""
        # Fonction non-linéaire avec bruit
        y_true = 2 * math.sin(x) + 0.5 * x + random.gauss(0, 0.2)
        y_pred = 2 * math.sin(x) + 0.5 * x
        uncertainty = abs(random.gauss(0.1, 0.05))
        
        return {
            "x": round(x, 4),
            "y_pred": round(y_pred, 4),
            "y_true": round(y_true, 4),
            "uncertainty": round(uncertainty, 4),
            "confidence": round(1 - uncertainty, 4)
        }

# ═══════════════════════════════════════════════════════════════
# 🔄 DATA PIPELINE SIMULATION
# ═══════════════════════════════════════════════════════════════

PIPELINE_STAGES = [
    {"id": "extract", "name": "Extract", "icon": "📥", "duration": (0.5, 1.5)},
    {"id": "validate", "name": "Validate", "icon": "✅", "duration": (0.3, 0.8)},
    {"id": "transform", "name": "Transform", "icon": "⚙️", "duration": (1.0, 2.5)},
    {"id": "enrich", "name": "Enrich", "icon": "✨", "duration": (0.5, 1.2)},
    {"id": "load", "name": "Load", "icon": "📤", "duration": (0.8, 1.8)},
    {"id": "index", "name": "Index", "icon": "🔍", "duration": (0.3, 0.7)},
]

class PipelineSimulator:
    """Simulates a data pipeline execution"""
    
    @staticmethod
    def generate_log(stage: str, status: str, message: str) -> dict:
        return {
            "timestamp": datetime.now().isoformat(),
            "stage": stage,
            "status": status,
            "message": message,
            "level": "INFO" if status == "running" else ("SUCCESS" if status == "completed" else "ERROR")
        }
    
    @staticmethod
    def generate_metrics() -> dict:
        return {
            "rows_processed": random.randint(10000, 100000),
            "rows_failed": random.randint(0, 50),
            "bytes_transferred": random.randint(1000000, 50000000),
            "cpu_usage": round(random.uniform(20, 85), 1),
            "memory_usage": round(random.uniform(30, 70), 1),
            "throughput": random.randint(5000, 25000)  # rows/sec
        }

# ═══════════════════════════════════════════════════════════════
# 📈 REAL-TIME DATA STREAMS
# ═══════════════════════════════════════════════════════════════

async def generate_metrics_stream():
    """SSE stream for real-time system metrics"""
    while True:
        data = {
            "timestamp": datetime.now().isoformat(),
            "cpu": round(random.uniform(15, 85), 1),
            "memory": round(random.uniform(40, 75), 1),
            "network_in": random.randint(100, 5000),
            "network_out": random.randint(50, 3000),
            "disk_io": random.randint(10, 500),
            "active_jobs": random.randint(1, 12),
            "queue_size": random.randint(0, 50),
            "latency_ms": round(random.uniform(5, 150), 2)
        }
        yield f"data: {json.dumps(data)}\n\n"
        await asyncio.sleep(1)

async def generate_ml_stream():
    """SSE stream for ML training simulation"""
    total_epochs = 50
    for epoch in range(1, total_epochs + 1):
        metrics = MLSimulator.generate_training_metrics(epoch, total_epochs)
        yield f"data: {json.dumps(metrics)}\n\n"
        await asyncio.sleep(0.3)
    # Signal completion
    yield f"data: {json.dumps({'status': 'completed', 'message': 'Training finished!'})}\n\n"

async def generate_prediction_stream():
    """SSE stream for live predictions"""
    x = 0
    while True:
        prediction = MLSimulator.predict_regression(x)
        yield f"data: {json.dumps(prediction)}\n\n"
        x += 0.1
        if x > 10:
            x = 0
        await asyncio.sleep(0.2)

async def generate_pipeline_stream():
    """SSE stream for pipeline execution"""
    run_id = f"run_{random.randint(1000, 9999)}"
    total_rows = random.randint(50000, 200000)
    
    yield f"data: {json.dumps({'type': 'start', 'run_id': run_id, 'total_rows': total_rows})}\n\n"
    
    for stage in PIPELINE_STAGES:
        # Stage starting
        log = PipelineSimulator.generate_log(stage["id"], "running", f"Starting {stage['name']}...")
        yield f"data: {json.dumps({'type': 'log', **log})}\n\n"
        await asyncio.sleep(0.2)
        
        # Progress updates
        duration = random.uniform(*stage["duration"])
        steps = int(duration / 0.1)
        for i in range(steps):
            progress = (i + 1) / steps * 100
            metrics = PipelineSimulator.generate_metrics()
            yield f"data: {json.dumps({'type': 'progress', 'stage': stage['id'], 'progress': round(progress, 1), 'metrics': metrics})}\n\n"
            await asyncio.sleep(0.1)
        
        # Stage completed
        log = PipelineSimulator.generate_log(stage["id"], "completed", f"{stage['name']} completed successfully")
        yield f"data: {json.dumps({'type': 'log', **log})}\n\n"
        await asyncio.sleep(0.1)
    
    # Pipeline completed
    yield f"data: {json.dumps({'type': 'complete', 'run_id': run_id, 'status': 'success', 'message': 'Pipeline completed successfully!'})}\n\n"

# ═══════════════════════════════════════════════════════════════
# 🛣️ API ROUTES
# ═══════════════════════════════════════════════════════════════

@app.get("/")
def read_root():
    return {
        "message": "🚀 Data Science Dashboard API",
        "version": "2.0.0",
        "endpoints": {
            "profile": "/profile",
            "skills": "/skills",
            "metrics_stream": "/stream/metrics",
            "ml_training": "/stream/training",
            "predictions": "/stream/predictions",
            "pipeline": "/stream/pipeline"
        }
    }

@app.get("/profile")
def get_profile():
    return PROFILE

@app.get("/skills")
def get_skills():
    return SKILLS

@app.get("/skills/{category}")
def get_skills_by_category(category: str):
    return [s for s in SKILLS if s["category"].lower() == category.lower()]

# SSE Streaming Endpoints
@app.get("/stream/metrics")
async def stream_metrics():
    """Real-time system metrics stream"""
    return StreamingResponse(
        generate_metrics_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@app.get("/stream/training")
async def stream_training():
    """ML training simulation stream"""
    return StreamingResponse(
        generate_ml_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@app.get("/stream/predictions")
async def stream_predictions():
    """Live prediction stream"""
    return StreamingResponse(
        generate_prediction_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@app.get("/stream/pipeline")
async def stream_pipeline():
    """Pipeline execution simulation stream"""
    return StreamingResponse(
        generate_pipeline_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

# Quick data endpoints (non-streaming)
@app.get("/data/sample")
def get_sample_data():
    """Generate sample dataset for visualization"""
    return {
        "scatter": [{"x": i, "y": 2 * math.sin(i/5) + random.gauss(0, 0.3)} for i in range(100)],
        "timeseries": [{"t": i, "value": 50 + 30 * math.sin(i/10) + random.gauss(0, 5)} for i in range(50)],
        "distribution": [random.gauss(50, 15) for _ in range(200)]
    }

@app.get("/data/realtime-snapshot")
def get_realtime_snapshot():
    """Get current metrics snapshot"""
    return {
        "timestamp": datetime.now().isoformat(),
        "system": {
            "cpu": round(random.uniform(15, 85), 1),
            "memory": round(random.uniform(40, 75), 1),
            "disk": round(random.uniform(20, 60), 1)
        },
        "jobs": {
            "running": random.randint(1, 5),
            "queued": random.randint(0, 20),
            "completed_today": random.randint(50, 200)
        },
        "data": {
            "rows_processed_today": random.randint(1000000, 10000000),
            "bytes_transferred": random.randint(10000000, 100000000)
        }
    }