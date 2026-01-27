from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import asyncio
import json
import random
import math
from datetime import datetime
from typing import Generator

app = FastAPI(title="🔥 EXTREME Data Science API")

origins = ["*"]

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
    {"name": "Python", "level": 95, "category": "Languages", "icon": "🐍", "color": "#3776ab"},
    {"name": "SQL", "level": 90, "category": "Languages", "icon": "🗃️", "color": "#f29111"},
    {"name": "Pandas", "level": 92, "category": "Data", "icon": "🐼", "color": "#150458"},
    {"name": "Scikit-learn", "level": 88, "category": "ML", "icon": "🤖", "color": "#f7931e"},
    {"name": "TensorFlow", "level": 75, "category": "ML", "icon": "🧠", "color": "#ff6f00"},
    {"name": "PyTorch", "level": 70, "category": "ML", "icon": "🔥", "color": "#ee4c2c"},
    {"name": "Apache Spark", "level": 80, "category": "Big Data", "icon": "⚡", "color": "#e25a1c"},
    {"name": "Docker", "level": 85, "category": "DevOps", "icon": "🐳", "color": "#2496ed"},
    {"name": "Kubernetes", "level": 65, "category": "DevOps", "icon": "☸️", "color": "#326ce5"},
    {"name": "Airflow", "level": 78, "category": "Orchestration", "icon": "🌬️", "color": "#017cee"},
    {"name": "FastAPI", "level": 88, "category": "Backend", "icon": "⚡", "color": "#009688"},
    {"name": "PostgreSQL", "level": 85, "category": "Databases", "icon": "🐘", "color": "#336791"},
    {"name": "MongoDB", "level": 72, "category": "Databases", "icon": "🍃", "color": "#47a248"},
    {"name": "Redis", "level": 70, "category": "Databases", "icon": "🔴", "color": "#dc382d"},
    {"name": "Git", "level": 90, "category": "Tools", "icon": "📦", "color": "#f05032"},
]

# ═══════════════════════════════════════════════════════════════
# � BLOG & PROJECTS
# ═══════════════════════════════════════════════════════════════

BLOG_POSTS = [
    {
        "id": 1,
        "title": "Optimizing Docker Images for Python",
        "date": "2024-03-15",
        "category": "DevOps",
        "summary": "How to reduce your container size from 1GB to 150MB using multi-stage builds and Alpine/Slim variants.",
        "content": "Full content would go here...",
        "read_time": "5 min"
    },
    {
        "id": 2,
        "title": "Understanding Attention Mechanisms",
        "date": "2024-02-28",
        "category": "Deep Learning",
        "summary": "A visual guide to how Transformers process sequences, from Self-Attention to Multi-Head Attention.",
        "content": "...",
        "read_time": "12 min"
    },
    {
        "id": 3,
        "title": "FastAPI + Vue 3: The Modern Stack",
        "date": "2024-01-10",
        "category": "Web Dev",
        "summary": "Why I chose FastAPI for backend performance and Vue 3 Composition API for frontend reactivity.",
        "content": "...",
        "read_time": "8 min"
    }
]

PROJECTS = [
    {
        "id": 101,
        "name": "Live Stock Predictor",
        "stack": ["Python", "TensorFlow", "Kafka"],
        "status": "Production",
        "description": "Real-time stock market prediction engine using LSTM networks processing 50k events/sec."
    },
    {
        "id": 102,
        "name": "Auto-ML Orchestrator",
        "stack": ["Kubernetes", "Airflow", "Docker"],
        "status": "Beta",
        "description": "Self-healing pipeline that automatically retrains models when data drift is detected."
    },
    {
        "id": 103,
        "name": "EcoVision",
        "stack": ["PyTorch", "Raspberry Pi", "OpenCV"],
        "status": "Completed",
        "description": "IoT device for detecting plastic waste in rivers using computer vision at the edge."
    }
]

# ═══════════════════════════════════════════════════════════════
# �🖥️ TERMINAL COMMANDS SIMULATION
# ═══════════════════════════════════════════════════════════════

TERMINAL_RESPONSES = {
    "help": """
╔══════════════════════════════════════════════════════════════╗
║  🚀 DATALAB TERMINAL v2.0 - Available Commands               ║
╠══════════════════════════════════════════════════════════════╣
║  help          - Show this help message                      ║
║  whoami        - Display user info                           ║
║  skills        - List technical skills                       ║
║  train         - Start ML model training                     ║
║  predict <n>   - Make n predictions                          ║
║  pipeline      - Run ETL pipeline                            ║
║  matrix        - Enter the Matrix 🐇                         ║
║  hack          - Initialize hacking sequence                 ║
║  stats         - Show system statistics                      ║
║  clear         - Clear terminal                              ║
║  neofetch      - System information                          ║
║  cowsay <msg>  - Cow says something                          ║
║  fortune       - Random fortune                              ║
╚══════════════════════════════════════════════════════════════╝""",
    "whoami": """
┌─────────────────────────────────────────┐
│  👤 Pierre Lafage                       │
│  📍 Data Scientist & Data Engineer      │
│  🔗 github.com/LPierre0                 │
│  💼 ML | Data Engineering | MLOps       │
└─────────────────────────────────────────┘""",
    "neofetch": """
        ⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀         pierre@datalab
      ⢀⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⡀       ──────────────────
     ⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦      OS: DataLab OS x86_64
    ⣾⣿⣿⣿⣿⣿⣿⣿⣿⡿⠿⠿⠿⠿⠿⠿⠿⠿⠿⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷     Host: Docker Container
   ⣿⣿⣿⣿⣿⣿⣿⠟⠁                ⠈⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿    Kernel: FastAPI 0.115
   ⣿⣿⣿⣿⣿⣿⠃    ⢀⣴⣿⣿⣿⣿⣦⡀    ⠘⣿⣿⣿⣿⣿⣿⣿⣿⣿    Uptime: Always grinding
   ⣿⣿⣿⣿⣿⣿    ⢰⣿⣿⣿⣿⣿⣿⣿⣿⡆    ⣿⣿⣿⣿⣿⣿⣿⣿⣿    Shell: Python 3.13
   ⣿⣿⣿⣿⣿⣿⡀    ⠻⣿⣿⣿⣿⣿⣿⠟    ⢀⣿⣿⣿⣿⣿⣿⣿⣿⣿    CPU: Neural Network
   ⣿⣿⣿⣿⣿⣿⣿⣄      ⠉⠉⠉⠉      ⣠⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿    Memory: Infinite
    ⢻⣿⣿⣿⣿⣿⣿⣿⣶⣤⣀⣀⣀⣀⣀⣀⣤⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟     GPU: RTX IMAGINATION
     ⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟      Disk: Unlimited Data
      ⠙⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠋       
        ⠉⠛⠿⠿⠿⠿⠿⠿⠿⠿⠿⠿⠿⠿⠿⠿⠿⠛⠉         🐍 Python  🐳 Docker  ⚡ FastAPI""",
}

FORTUNES = [
    "The best model is the one that ships to production.",
    "In data we trust, but verify with tests.",
    "A clean dataset is worth a thousand features.",
    "Overfitting is just memorizing the past.",
    "The cloud is just someone else's GPU.",
    "Machine learning is just spicy statistics.",
    "Your neural network is only as good as your data.",
    "pip install happiness --upgrade",
    "SELECT * FROM life WHERE stress = 0;  -- 0 rows returned",
    "git commit -m 'fixed bug' (narrator: he had not fixed the bug)",
]

# ═══════════════════════════════════════════════════════════════
# 🔬 MACHINE LEARNING SIMULATION
# ═══════════════════════════════════════════════════════════════

class MLSimulator:
    @staticmethod
    def generate_training_metrics(epoch: int, total_epochs: int) -> dict:
        progress = epoch / total_epochs
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
            "throughput": random.randint(5000, 25000)
        }

# ═══════════════════════════════════════════════════════════════
# 📈 REAL-TIME DATA STREAMS
# ═══════════════════════════════════════════════════════════════

async def generate_metrics_stream():
    while True:
        data = {
            "timestamp": datetime.now().isoformat(),
            "cpu": round(random.uniform(15, 85), 1),
            "memory": round(random.uniform(40, 75), 1),
            "gpu": round(random.uniform(0, 100), 1),
            "network_in": random.randint(100, 5000),
            "network_out": random.randint(50, 3000),
            "disk_io": random.randint(10, 500),
            "active_jobs": random.randint(1, 12),
            "queue_size": random.randint(0, 50),
            "latency_ms": round(random.uniform(5, 150), 2),
            "requests_per_sec": random.randint(100, 5000),
            "error_rate": round(random.uniform(0, 2), 2),
            "temperature": round(random.uniform(45, 85), 1),
        }
        yield f"data: {json.dumps(data)}\n\n"
        await asyncio.sleep(0.5)

async def generate_ml_stream():
    while True:
        total_epochs = 100
        for epoch in range(1, total_epochs + 1):
            metrics = MLSimulator.generate_training_metrics(epoch, total_epochs)
            yield f"data: {json.dumps(metrics)}\n\n"
            await asyncio.sleep(0.15)
        yield f"data: {json.dumps({'status': 'completed', 'message': 'Training sequence finished. Restarting...'})}\n\n"
        await asyncio.sleep(2)

async def generate_prediction_stream():
    x = 0
    while True:
        prediction = MLSimulator.predict_regression(x)
        yield f"data: {json.dumps(prediction)}\n\n"
        x += 0.1
        if x > 10:
            x = 0
        await asyncio.sleep(0.1)

async def generate_pipeline_stream():
    while True:
        run_id = f"run_{random.randint(1000, 9999)}"
        total_rows = random.randint(50000, 200000)
        
        yield f"data: {json.dumps({'type': 'start', 'run_id': run_id, 'total_rows': total_rows})}\n\n"
        
        for stage in PIPELINE_STAGES:
            log = PipelineSimulator.generate_log(stage["id"], "running", f"Starting {stage['name']}...")
            yield f"data: {json.dumps({'type': 'log', **log})}\n\n"
            await asyncio.sleep(0.2)
            
            duration = random.uniform(*stage["duration"])
            steps = int(duration / 0.1)
            for i in range(steps):
                progress = (i + 1) / steps * 100
                metrics = PipelineSimulator.generate_metrics()
                yield f"data: {json.dumps({'type': 'progress', 'stage': stage['id'], 'progress': round(progress, 1), 'metrics': metrics})}\n\n"
                await asyncio.sleep(0.1)
            
            log = PipelineSimulator.generate_log(stage["id"], "completed", f"{stage['name']} completed successfully")
            yield f"data: {json.dumps({'type': 'log', **log})}\n\n"
            await asyncio.sleep(0.1)
        
        yield f"data: {json.dumps({'type': 'complete', 'run_id': run_id, 'status': 'success', 'message': 'Pipeline completed successfully!'})}\n\n"
        await asyncio.sleep(3)

async def generate_matrix_stream():
    """Stream Matrix-style characters"""
    chars = "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ0123456789ABCDEF"
    columns = 80
    while True:
        line = ''.join(random.choice(chars) for _ in range(columns))
        yield f"data: {json.dumps({'line': line, 'highlight': random.randint(0, columns-1)})}\n\n"
        await asyncio.sleep(0.05)

async def generate_hack_stream():
    """Simulated hacking sequence"""
    messages = [
        ("INIT", "Initializing neural interface..."),
        ("SCAN", "Scanning network topology..."),
        ("FOUND", "Found 12 active nodes"),
        ("PROBE", "Probing target systems..."),
        ("CRACK", "Decrypting security protocols..."),
        ("BYPASS", "Bypassing firewall [████████░░] 80%"),
        ("BYPASS", "Bypassing firewall [██████████] 100%"),
        ("ACCESS", "Root access granted!"),
        ("EXTRACT", "Extracting data packages..."),
        ("DOWNLOAD", "Download complete"),
        ("CLEAN", "Cleaning traces..."),
        ("DONE", "Mission accomplished! 🎯"),
        ("WAIT", "Pending new target..."),
    ]
    
    while True:
        for tag, msg in messages:
            yield f"data: {json.dumps({'tag': tag, 'message': msg, 'timestamp': datetime.now().isoformat()})}\n\n"
            await asyncio.sleep(random.uniform(0.5, 2.0))
        # Loop indefinitely
        await asyncio.sleep(2)

async def generate_3d_data_stream():
    """Stream 3D visualization data points"""
    t = 0
    while True:
        points = []
        for i in range(50):
            angle = t + i * 0.1
            r = 2 + math.sin(t * 0.5 + i * 0.2)
            points.append({
                "x": r * math.cos(angle),
                "y": r * math.sin(angle),
                "z": math.sin(t * 0.3 + i * 0.1) * 2,
                "color": f"hsl({(t * 50 + i * 10) % 360}, 70%, 60%)",
                "size": 0.1 + abs(math.sin(t + i)) * 0.1
            })
        
        yield f"data: {json.dumps({'points': points, 't': t})}\n\n"
        t += 0.05
        await asyncio.sleep(0.03)

# ═══════════════════════════════════════════════════════════════
# 🛣️ API ROUTES
# ═══════════════════════════════════════════════════════════════

@app.get("/")
def read_root():
    return {
        "message": "🔥 EXTREME Data Science Dashboard API",
        "version": "3.0.0-EXTREME",
        "power_level": "OVER 9000"
    }

@app.get("/profile")
def get_profile():
    return PROFILE

@app.get("/skills")
def get_skills():
    return SKILLS

@app.get("/pipeline")
def get_pipeline_info():
    return {"stages": PIPELINE_STAGES}

@app.get("/blog")
def get_blog_posts():
    return BLOG_POSTS

@app.get("/projects")
def get_projects():
    return PROJECTS

@app.get("/terminal/{command}")
def execute_terminal(command: str):
    cmd = command.lower().strip()
    
    if cmd in TERMINAL_RESPONSES:
        return {"output": TERMINAL_RESPONSES[cmd], "success": True}
    elif cmd == "fortune":
        return {"output": f"\n  🔮 {random.choice(FORTUNES)}\n", "success": True}
    elif cmd.startswith("cowsay"):
        msg = cmd[7:].strip() or "Moo!"
        cow = f"""
   {'_' * (len(msg) + 2)}
  < {msg} >
   {'-' * (len(msg) + 2)}
          \\   ^__^
           \\  (oo)\\_______
              (__)\\       )\\/\\
                  ||----w |
                  ||     ||
"""
        return {"output": cow, "success": True}
    elif cmd == "stats":
        stats = f"""
╔════════════════════════════════════════╗
║  📊 SYSTEM STATISTICS                  ║
╠════════════════════════════════════════╣
║  CPU Cores:     {random.randint(8, 64):>4}                  ║
║  GPU Memory:    {random.randint(8, 80):>4} GB               ║
║  RAM:           {random.randint(32, 512):>4} GB               ║
║  Storage:       {random.randint(1, 10):>4} TB                ║
║  Models Trained: {random.randint(100, 9999):>4}                ║
║  Data Processed: {random.randint(1, 100):>4} PB               ║
║  Coffee Consumed: {random.randint(1000, 9999):>4} cups          ║
╚════════════════════════════════════════╝"""
        return {"output": stats, "success": True}
    elif cmd == "skills":
        output = "\n  🛠️  TECHNICAL SKILLS\n  " + "─" * 30 + "\n"
        for skill in SKILLS[:8]:
            bar = "█" * (skill["level"] // 10) + "░" * (10 - skill["level"] // 10)
            output += f"  {skill['icon']} {skill['name']:<12} [{bar}] {skill['level']}%\n"
        return {"output": output, "success": True}
    elif cmd == "train":
        return {"output": "🚀 INITIATING TRAINING SEQUENCE...\n\nEpoch 1/5 [==>.......] loss: 0.8242 acc: 0.45\nEpoch 2/5 [====>.....] loss: 0.6120 acc: 0.68\nEpoch 3/5 [======>...] loss: 0.4021 acc: 0.79\nEpoch 4/5 [========>.] loss: 0.2201 acc: 0.88\nEpoch 5/5 [==========] loss: 0.0912 acc: 0.96\n\n✨ MODEL SAVED: weights_v1.pth", "success": True}
    elif cmd.startswith("predict"):
        return {"output": f"🔍 INPUT AGGREGATED.\n   Running inference...\n   Probabilities: [0.01, 0.98, 0.01]\n   RESULT: POSITIVE (Confidence: 98%)", "success": True}
    elif cmd == "pipeline":
        return {"output": "⚙️  ETL PIPELINE STARTED\n   [EXTRACT] Connecting to Data Lake... OK (2ms)\n   [TRANSFORM] Normalizing Tensors... OK (15ms)\n   [LOAD] Pushing to VectorDB... OK (42ms)\n   ✅ PIPELINE FINISHED SUCCESSFULLY", "success": True}
    elif cmd == "matrix":
        return {"output": "\n  Wake up, Neo...\n  The Matrix has you.\n  Follow the white rabbit.\n  🐇\n", "success": True}
    elif cmd == "hack":
        return {"output": "💀 HACK STATUS:\n   TARGET: MAINFRAME\n   [||||||||||] BRUTE FORCE SSH... SUCCESS\n   [||||||||||] INJECTING SHELL... SUCCESS\n   [||||||||||] ESCALATING PRIVILEGES... ROOT\n   ABORTING - TRACE DETECTED.", "success": True}
    else:
        return {"output": f"  ❌ Command not found: {command}\n  Type 'help' for available commands", "success": False}

# SSE Streaming Endpoints
@app.get("/stream/metrics")
async def stream_metrics():
    return StreamingResponse(
        generate_metrics_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"}
    )

@app.get("/stream/training")
async def stream_training():
    return StreamingResponse(
        generate_ml_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"}
    )

@app.get("/stream/predictions")
async def stream_predictions():
    return StreamingResponse(
        generate_prediction_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"}
    )

@app.get("/stream/pipeline")
async def stream_pipeline():
    return StreamingResponse(
        generate_pipeline_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"}
    )

@app.get("/stream/matrix")
async def stream_matrix():
    return StreamingResponse(
        generate_matrix_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"}
    )

@app.get("/stream/hack")
async def stream_hack():
    return StreamingResponse(
        generate_hack_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"}
    )

@app.get("/stream/3d")
async def stream_3d():
    return StreamingResponse(
        generate_3d_data_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"}
    )

@app.get("/data/sample")
def get_sample_data():
    return {
        "scatter": [{"x": i, "y": 2 * math.sin(i/5) + random.gauss(0, 0.3)} for i in range(100)],
        "timeseries": [{"t": i, "value": 50 + 30 * math.sin(i/10) + random.gauss(0, 5)} for i in range(50)],
        "distribution": [random.gauss(50, 15) for _ in range(200)]
    }