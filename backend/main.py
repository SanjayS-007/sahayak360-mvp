import socket
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

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
from api.routes_alerts import router as alerts_router
from api.routes_admin_analytics import router as admin_analytics_router
from api.routes_practice import router as practice_router
from api.routes_notifications import router as notifications_router
from api.routes_gamification import router as gamification_router

app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(ingest_router, prefix="/api/ingest", tags=["Data Ingestion"])
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(query_router, prefix="/api/query", tags=["AI Query"])
app.include_router(quiz_router, prefix="/api/quiz", tags=["Quiz"])
app.include_router(websocket_router, prefix="/api/ws", tags=["WebSocket"])
app.include_router(alerts_router, prefix="/api/alerts", tags=["Alerts & Interventions"])
app.include_router(admin_analytics_router, prefix="/api/admin/analytics", tags=["Admin Analytics"])
app.include_router(practice_router, prefix="/api/practice", tags=["Practice"])
app.include_router(notifications_router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(gamification_router, prefix="/api/gamification", tags=["Gamification"])


def _is_database_unavailable(exc: BaseException) -> bool:
    current: BaseException | None = exc
    seen: set[int] = set()
    markers = (
        "name or service not known",
        "getaddrinfo",
        "could not connect",
        "connection refused",
        "ssl connection has been closed",
        "timeout",
        "network is unreachable",
    )
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        text = str(current).lower()
        if isinstance(current, (ConnectionError, TimeoutError, socket.gaierror)):
            return True
        if type(current).__name__ in {"OperationalError", "InterfaceError"} and any(
            marker in text for marker in markers
        ):
            return True
        current = current.__cause__ or current.__context__
    return False


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import logging, traceback
    from fastapi import HTTPException as FastAPIHTTPException
    from starlette.exceptions import HTTPException as StarletteHTTPException

    if isinstance(exc, (FastAPIHTTPException, StarletteHTTPException)):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    logging.getLogger("sahayak360").error(f"Unhandled: {exc}\n{traceback.format_exc()}")
    if _is_database_unavailable(exc):
        return JSONResponse(
            status_code=503,
            content={"detail": "Sign-in is unavailable because the database cannot be reached."},
        )
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/", tags=["Health"])
async def root():
    return {"status": "healthy", "service": "sahayak-360-api", "version": "1.0.0"}


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "service": "sahayak-360-api", "version": "1.0.0"}
