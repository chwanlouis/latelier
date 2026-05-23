import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from tools.log import LoggingMiddleware
from tools.settings import settings
from router.auth_router import auth_router


app = FastAPI(title="L'atelier")
app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[f"http://localhost:{settings.FRONTEND_PORT}"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router, tags=["Auth"])


@app.get(path="/healthCheck", tags=["Health"])
async def health_check(request: Request):
    return {"status": "ok", "message": "Service is healthy"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=settings.BACKEND_PORT, reload=True)