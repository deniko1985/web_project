import os
import mimetypes
from datetime import datetime
from typing import Annotated
import pytz
from fastapi import APIRouter, HTTPException, Depends, Response, Request, Form, Path
from fastapi.responses import RedirectResponse
from typing import List
from starlette.templating import Jinja2Templates
import starlette.status as status

from schemas.users import User
from schemas.notes import UserNotesBase
from db import notes
from utils.depend import get_user_by_cookie, get_timezone_by_cookie
from utils.depend import CurrentUser, DBSession


router = APIRouter()
templates = Jinja2Templates(directory="/backend/ui")


@router.get('/notes')
async def get_notes_page(
        request: Request,
        db: DBSession,
        current_user: CurrentUser,
        tz: User = Depends(get_timezone_by_cookie)):
    date = datetime.now().astimezone(pytz.timezone(tz)).strftime("%d.%m.%Y")
    if current_user:
        return templates.TemplateResponse(
            "/notes.html",
            {"request": request, "id": current_user.id, "date": date})
    else:
        raise HTTPException(status_code=401, detail="Not authenticated")


@router.get('/my_notes/{page_number}', response_model=List[UserNotesBase])
async def get_my_notes_page(
        request: Request,
        page_number: Annotated[int, Path(ge=1)],
        db: DBSession,
        current_user: CurrentUser,
        tz: User = Depends(get_timezone_by_cookie)):
    if current_user:
        data_notes = await notes.get_all_notes(db, current_user.id, tz, page_number)
        if data_notes:
            return templates.TemplateResponse(
                "/my_notes.html",
                {"request": request, "data_notes": data_notes})
        else:
            return templates.TemplateResponse(
                "/modal_error.html",
                {"request": request, "data": "Нет заметок"})
    else:
        raise HTTPException(status_code=401, detail="Not authenticated")


@router.post('/add_note')
async def add_note_user(
        request: Request,
        db: DBSession,
        current_user: CurrentUser,
        name_notes=Form(),
        text_notes=Form()):
    user_id = current_user.id
    user_name = current_user.username
    data_note = await notes.create_note_user(db, user_id, user_name, name_notes, text_notes)
    if not data_note:
        return templates.TemplateResponse(
            "/modal_error.html",
            {"request": request, "data": "Нет заметок"})
    else:
        return RedirectResponse(
                    '/notes',
                    status_code=status.HTTP_302_FOUND)


@router.get('/delete_note/{note_id}')
async def delete_note_user(
        request: Request,
        note_id: int,
        db: DBSession,
        current_user: CurrentUser,):
    user_id = current_user.id
    data = await notes.delete_note(db, user_id, note_id)
    if data:
        return templates.TemplateResponse(
            "/modal_error.html",
            {"request": request, "data": "Удаление не удалось"})
    else:
        return RedirectResponse('/my_notes/1')


@router.get('/update_note/{id}')
async def get_update_note_page(
        id: int,
        request: Request,
        db: DBSession,
        current_user: CurrentUser,):
    date = datetime.now().strftime("%d-%m-%Y")
    user_id = current_user.id
    data = await notes.get_note_by_id(db, id, user_id)
    if current_user:
        return templates.TemplateResponse(
            "/edit_note.html",
            {"request": request, "data": data, "date": date})
    else:
        raise HTTPException(status_code=401, detail="Not authenticated")


@router.post('/update_note')
async def get_update_note(
        request: Request,
        db: DBSession,
        current_user: CurrentUser,
        id=Form(),
        name_notes=Form(),
        text_notes=Form(),
        lang=Form()):
    user_id = current_user.id
    data = await notes.update_note_by_id(db, user_id, int(id), name_notes[:76], text_notes, lang)
    if data:
        return RedirectResponse(
            '/my_notes/1',
            status_code=status.HTTP_302_FOUND)
    else:
        return templates.TemplateResponse(
            "/modal_error.html",
            {"request": request, "data": "Обновление не удалось"})


@router.get("/download_note/{note_id}")
async def download_note(
        request: Request,
        note_id: int,
        db: DBSession,
        current_user: CurrentUser,):
    if current_user:
        load_filepath = await notes.create_note_file(db, current_user.id, note_id)
        mimetype = mimetypes.guess_type(load_filepath)[0]
        with open(load_filepath, 'rb') as fs:
            data_file = fs.read()
            os.remove(load_filepath)
        if not data_file:
            return templates.TemplateResponse(
                "/modal_error.html",
                {"request": request, "data": "Создание файла не удалось"})
        else:
            return Response(
                content=data_file,
                media_type=mimetype,
                headers={"Content-Disposition": f'attachment; filename={load_filepath}'}
            )
    else:
        raise HTTPException(status_code=401, detail="Not authenticated")


@router.get("/search_by_notes/{search_query}")
async def get_search_query(
        request: Request,
        search_text: str,
        page: int,
        db: DBSession,
        current_user: CurrentUser,
        search_by_name='off',
        search_by_text='off',
        tz: User = Depends(get_timezone_by_cookie)) -> list:
    if search_by_name == 'off' and search_by_text == 'off' or not search_text:
        return templates.TemplateResponse(
            "/modal_error.html",
            {"request": request, "data": "Вы не можете совершить поиск не введя текст или со снятыми флажками"})
    user_id = current_user.id
    result = await notes.get_all_notes(
        db,
        user_id,
        tz,
        page,
        str(search_text),
        search_by_name,
        search_by_text
    )
    if current_user:
        if result:
            return templates.TemplateResponse(
                "/search_note.html",
                {
                    "request": request,
                    "data": result,
                    "search_text": search_text,
                    "search_by_name": search_by_name,
                    "search_by_text": search_by_text
                })
        else:
            return templates.TemplateResponse(
                "/modal_error.html",
                {"request": request, "data": "По вашему запросу не найдено ни одной записи"})
    else:
        raise HTTPException(status_code=401, detail="Not authenticated")


@router.post("/add_favour")
async def add_favour(
        request: Request,
        db: DBSession,
        current_user: CurrentUser,
        add_favour=Form(default=None),
        id=Form()):
    user_id = current_user.id
    result = await notes.add_note_favour(db, user_id, int(id), add_favour)
    if result:
        return RedirectResponse('/my_notes/1', status_code=status.HTTP_302_FOUND)
    else:
        raise HTTPException(status_code=400, detail="Добавление в избранное не удалось")


@router.get('/database_regeneration')
async def database_regeneration(db: DBSession):
    data_notes = await notes.regeneration()
    return data_notes


@router.get('/database_regeneration_lang')
async def database_regeneration_lang(db: DBSession):
    data_notes = await notes.regeneration_lang()
    return data_notes
