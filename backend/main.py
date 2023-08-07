from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import HTTPException
from fastapi.openapi.docs import (
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
import logging

from routes import budget, users, notes
from schemas.users import User
from utils.depend import get_user_by_cookie

templates = Jinja2Templates(directory="/backend/ui")


async def not_autorization(request: Request, exc: HTTPException):
    return templates.TemplateResponse('error/401.html', {'request': request}, status_code=401)


async def not_found_error(request: Request, exc: HTTPException):
    return templates.TemplateResponse('error/404.html', {'request': request}, status_code=404)


async def unprocessable_entity(request: Request, exc: HTTPException):
    return templates.TemplateResponse('error/50x.html', {'request': request}, status_code=422)


async def internal_error(request: Request, exc: HTTPException):
    return templates.TemplateResponse('error/50x.html', {'request': request}, status_code=500)


exception_handlers = {
    401: not_autorization,
    404: not_found_error,
    422: unprocessable_entity,
    500: internal_error,
    501: internal_error,
    502: internal_error,
}

app = FastAPI(docs_url=None, exception_handlers=exception_handlers)

app.mount("/ui", StaticFiles(directory="./ui"), name="ui")
app.mount("/ui/static/css", StaticFiles(directory="./ui/static/css"), name="css")
app.mount("/ui/static/images", StaticFiles(directory="./ui/static/images"), name="images")


# loop = asyncio.get_event_loop()


app.include_router(users.router)
app.include_router(notes.router)
app.include_router(budget.router)


origins = ([
    "http://localhost:6001",
    "http://localhost:6002",
    "https://test.deniko1985.ru"
])

app.add_middleware(
    CORSMiddleware,
    # allow_origins=origins,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    filename="./logs/app_log.log",
    filemode="w",
    format="%(asctime)s %(levelname)s %(message)s"
)
logging.debug("A DEBUG Message")
logging.info("An INFO")
logging.warning("A WARNING")
logging.error("An ERROR")
logging.critical("A message of CRITICAL severity")


@app.on_event("startup")
async def startup():
    # await database.connect()
    pass


@app.on_event("shutdown")
async def shutdown():
    # await database.close()
    pass


@app.get('/index')
async def index(request: Request, current_user: User = Depends(get_user_by_cookie)):
    x = 'x-forwarded-for'.encode('utf-8')
    for header in request.headers.raw:
        if header[0] == x:
            print("Find out the forwarded-for ip address")
            forward_ip = header[1].decode('utf-8')
            print("forward_ip: ", forward_ip)
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
