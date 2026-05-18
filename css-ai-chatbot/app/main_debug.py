import os
import sys
import traceback
import uvicorn
import logging
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request

# Configuration du logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Création de l'app FastAPI
app = Starlette(debug=True)

# Configuration CORS permissive pour le debug
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.route("/", methods=["GET"])
async def root(request: Request):
    return JSONResponse({
        "message": "CSS RAG API - Mode Debug",
        "status": "running",
        "debug": True
    })

@app.route("/health", methods=["GET"])
async def health_check(request: Request):
    try:
        return JSONResponse({
            "status": "healthy",
            "debug_mode": True,
            "environment": {
                "python_version": sys.version,
                "redis_host": os.getenv("REDIS_HOST", "non défini"),
                "redis_port": os.getenv("REDIS_PORT", "non défini"),
                "openai_key_set": bool(os.getenv("OPENAI_API_KEY")),
                "deepseek_key_set": bool(os.getenv("DEEPSEEK_API_KEY")),
            }
        })
    except Exception as e:
        logger.error(f"Erreur health check: {e}")
        return JSONResponse({"status": "unhealthy", "error": str(e)}, status_code=500)

@app.route("/query", methods=["POST"])
async def simple_query(request: Request):
    try:
        data = await request.json()
        question = data.get("question", "")
        if not question:
            return JSONResponse({"detail": "Question manquante"}, status_code=400)

        return JSONResponse({
            "response": f"Debug: Votre question était '{question}'. L'API fonctionne correctement!",
            "sources": [],
            "debug_info": {
                "question_received": question,
                "timestamp": "debug",
                "mode": "debug_simple"
            }
        })
    except Exception as e:
        logger.error(f"Erreur query: {e}")
        logger.error(traceback.format_exc())
        return JSONResponse({
            "error": str(e),
            "traceback": traceback.format_exc(),
            "debug": True
        }, status_code=500)

@app.route("/debug/env", methods=["GET"])
async def debug_environment(request: Request):
    try:
        env_vars = {}
        for key in os.environ:
            if any(keyword in key.upper() for keyword in ['REDIS', 'API', 'SECRET', 'TOKEN', 'KEY']):
                if 'PASSWORD' in key.upper() or 'SECRET' in key.upper() or 'KEY' in key.upper():
                    env_vars[key] = "***MASQUÉ***" if os.environ.get(key) else "NON DÉFINI"
                else:
                    env_vars[key] = os.environ[key]

        return JSONResponse({
            "environment_variables": env_vars,
            "python_path": sys.path,
            "working_directory": os.getcwd()
        })
    except Exception as e:
        logger.error(f"Erreur debug env: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)

async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Exception globale: {exc}")
    logger.error(traceback.format_exc())
    return JSONResponse({
        "error": str(exc),
        "traceback": traceback.format_exc(),
        "debug": True,
        "request_url": str(request.url)
    }, status_code=500)

app.add_exception_handler(Exception, global_exception_handler)

if __name__ == "__main__":
    logger.info("Démarrage de l'API en mode debug")
    uvicorn.run(
        "app.main_debug:app",
        host="0.0.0.0",
        port=8000,
        log_level="debug",
        reload=True
    )