import uvicorn
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from tools.log import LoggingMiddleware
from tools.settings import settings
from router.auth_router import auth_router, permission_required, get_current_user
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles


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
app.mount("/template", StaticFiles(directory="template"), name="template")

@app.get(path="/healthCheck", tags=["Health"])
async def health_check(request: Request):
    return {"status": "ok", "message": "Service is healthy"}


@app.get(path="/", response_class=HTMLResponse, tags=["Demo"])
@app.get(path="/index.html", response_class=HTMLResponse, tags=["Demo"])
async def demo_index_page(request: Request):
    with open("template/index.html", "r", encoding="utf-8") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)


@app.get(path="/recipe", response_class=HTMLResponse, tags=["Demo"])
@app.get(path="/recipe.html", response_class=HTMLResponse, tags=["Demo"])
async def demo_recipe_page(request: Request):
    with open("template/recipe.html", "r", encoding="utf-8") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=settings.BACKEND_PORT, reload=True)