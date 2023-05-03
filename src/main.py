from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.openapi.docs import (
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from models.db import database
import asyncio

from routes import budget, users, notes
from schemas.users import User
from utils.depend import get_user_by_cookie


app = FastAPI(docs_url=None)
app.mount("/ui", StaticFiles(directory="./ui"), name="ui")
app.mount("/ui/static/css", StaticFiles(directory="./ui/static/css"), name="css")
app.mount("/ui/static/images", StaticFiles(directory="./ui/static/images"), name="images")


loop = asyncio.get_event_loop()


app.include_router(users.router)
app.include_router(notes.router)
app.include_router(budget.router)


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get('/index')
async def index(current_user: User = Depends(get_user_by_cookie)):
    if current_user:
        return RedirectResponse('/users')
    else:
        return FileResponse("ui/index.html")


@app.get("/")
async def old():
    return RedirectResponse("/index")


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="./ui/scripts/swagger-ui-bundle.js",
        swagger_css_url="./ui/static/css/swagger-ui.css",
    )


@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()
