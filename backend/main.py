from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from db.postgres import init_db, close_db, engine
from db.neo4j_driver import get_neo4j_driver, close_neo4j, init_neo4j_schema
from api.routes_websocket import ws_manager as student_ws_manager


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

    async def send_personal(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)


manager = ConnectionManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize databases (graceful if unavailable)
    import logging
    logger = logging.getLogger("sahayak360")

    try:
        await init_db()
        logger.info("PostgreSQL connected")
    except Exception as e:
        logger.warning(f"PostgreSQL unavailable: {e}. Running without DB.")

    try:
        app.state.neo4j_driver = await get_neo4j_driver()
        await init_neo4j_schema()
        logger.info("Neo4j connected")
    except Exception as e:
        app.state.neo4j_driver = None
        logger.warning(f"Neo4j unavailable: {e}. Running without graph DB.")

    app.state.ws_manager = student_ws_manager
    yield
    # Shutdown: close connections
    try:
        await close_db()
    except Exception:
        pass
    try:
        await close_neo4j()
    except Exception:
        pass


app = FastAPI(
    title="Sahayak 360 API",
    description="AI-powered educational analytics platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
from api.routes_auth import router as auth_router
from api.routes_ingest import router as ingest_router
from api.routes_dashboard import router as dashboard_router
from api.routes_query import router as query_router
from api.routes_quiz import router as quiz_router
from api.routes_websocket import router as websocket_router

app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(ingest_router, prefix="/api/ingest", tags=["Data Ingestion"])
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(query_router, prefix="/api/query", tags=["AI Query"])
app.include_router(quiz_router, prefix="/api/quiz", tags=["Quiz"])
app.include_router(websocket_router, prefix="/api/ws", tags=["WebSocket"])


@app.get("/", tags=["Health"])
async def health_check():
    return {"status": "healthy", "service": "sahayak-360-api", "version": "1.0.0"}
