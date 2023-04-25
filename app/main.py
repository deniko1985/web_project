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
app.mount("/main", StaticFiles(directory="./main"), name="main")
app.mount("/main/static/css", StaticFiles(directory="./main/static/css"), name="css")
app.mount("/main/static/images", StaticFiles(directory="./main/static/images"), name="images")


loop = asyncio.get_event_loop()


app.include_router(users.router)
app.include_router(notes.router)
app.include_router(budget.router)


@app.on_event("startup")
async def startup():
    await database.connect()
    # await users.start()
    # asyncio.ensure_future(users.start(loop))


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get('/index')
async def index(current_user: User = Depends(get_user_by_cookie)):
    if current_user:
        return RedirectResponse('/users')
    else:
        return FileResponse("main/index.html")


@app.get("/")
async def old():
    return RedirectResponse("/index")


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="./main/scripts/swagger-ui-bundle.js",
        swagger_css_url="./main/static/css/swagger-ui.css",
    )


@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


# @app.get("/doc#")
# async def openapi():
#     return app.openapi_schema

# @app.get('/')
# async def monitoring():
#   return {"status": "ok"}


# if __name__ == '__main__':
#    config = uvicorn.Config("main:app", host='0.0.0.0', port=5001, reload=True, # proxy_headers=True, log_level="info")
#    server = uvicorn.Server(config)
#    server.run()
