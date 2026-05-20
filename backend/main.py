import uvicorn
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from tools.log import LoggingMiddleware
from tools.settings import settings
from router.auth import auth_router, permission_required, get_current_user
from fastapi.responses import HTMLResponse


app = FastAPI(title="L'atelier")
app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router, tags=["Auth"])


@app.get(path="/healthCheck", tags=["Health"])
async def health_check(request: Request):
    return {"status": "ok", "message": "Service is healthy"}


@app.get(path="/demo", response_class=HTMLResponse, tags=["Demo"])
async def demo_page(request: Request):
    with open("template/index.html", "r", encoding="utf-8") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=settings.BACKEND_PORT, reload=True)