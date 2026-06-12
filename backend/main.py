import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from module.core.tools.log import LoggingMiddleware
from module.core.tools.settings import app_settings
from module.core.router.auth_router import auth_router
from module.core.router.admin_router import admin_service_router
from module.core.tools.psqltools import psql_manager
from module.core.tools.constants import api_constants
from module.knowledge_graph.router.foodb import foodb_router
from module.knowledge_graph.tools.neo4jtools import neo4j_manager
from module.core.scripts.init_admin import create_initial_admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    await psql_manager.initialize_and_verify(app_settings)
    await neo4j_manager.initialize_ogm()
    await create_initial_admin()
    yield
    await psql_manager.close_pool()


app = FastAPI(
    title=app_settings.APPLICATION_NAME,
    version=app_settings.VERSION,
    lifespan=lifespan
)

app.add_middleware(LoggingMiddleware)

origins = [
    f"http://localhost:{app_settings.FRONTEND_PORT}",
    "http://localhost"
]

if app_settings.CLOUD_BASE_URL:
    origins.append(app_settings.CLOUD_BASE_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router, prefix=api_constants.V1_PREFIX, tags=["Auth"])
app.include_router(admin_service_router, prefix=api_constants.V1_PREFIX, tags=["AdminSystem"])
app.include_router(foodb_router, prefix=api_constants.V1_PREFIX, tags=["FooDB"])


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=app_settings.BACKEND_PORT
    )
