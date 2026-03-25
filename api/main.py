import os
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from io import BytesIO

BASE_DIR = Path(__file__).resolve().parent.parent

CANDIDATES = [
        BASE_DIR,
        BASE_DIR.parent.parent.parent,
]
for p in CANDIDATES:
        if (p / "core").exists() and str(p) not in sys.path:
                    sys.path.insert(0, str(p))
                    break

from core.database import DatabaseSession
from api.routers import auth, vendas, financeiro, agenda, assinatura

app = FastAPI(title="Grupo Band - API", version="4.0.0")

app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(vendas.router)
app.include_router(financeiro.router)
app.include_router(agenda.router)
app.include_router(assinatura.router)

WEB_DIR = BASE_DIR / "web"

@app.get("/")
def read_index():
        index_path = WEB_DIR / "index_v2.html"
        return FileResponse(str(index_path))

if WEB_DIR.exists():
        app.mount("/web", StaticFiles(directory=str(WEB_DIR)), name="web")

@app.get("/status")
def status():
        return {"status": "online", "system": "Grupo Band 4.0", "version": "4.0.0"}

if __name__ == "__main__":
        import uvicorn
        port = int(os.environ.get("PORT", 8000))
        uvicorn.run("api.main:app", host="0.0.0.0", port=port, reload=False)
    
