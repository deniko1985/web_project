from datetime import datetime
import pytz
import uuid
from sqlalchemy import desc, func, or_, select, insert, delete, update
from sqlalchemy.exc import SQLAlchemyError
import math
import py3langid as langid
import logging

from models.notes import Notes
from models.databases import database
from schemas.notes import GetNotes
from utils import parsing_text


# получение пользовательского логгера и установка уровня логирования
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# настройка обработчика и форматировщика в соответствии с нашими нуждами
handler = logging.FileHandler(f"logs/{__name__}.log", mode='w')
formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")

# добавление форматировщика к обработчику
handler.setFormatter(formatter)
# добавление обработчика к логгеру
logger.addHandler(handler)

logger.info(f"Testing the custom logger for module {__name__}...")


class Note():

    @staticmethod
    def from_db(record: dict, tz: str):
        note = (GetNotes(**record)).dict()
        date = note["date"].astimezone(pytz.timezone(tz))
        note["date"] = date.strftime("%d-%m-%Y %H:%M")
        return note


async def get_all_notes(
        user_id,
        tz,
        page_number,
        search_text=None,
        search_by_name="off",
        search_by_text="off"):
    try:
        PAGE_SIZE = 9
        offset = (page_number - 1) * PAGE_SIZE
        cond = []
        if search_by_name == 'on':
            cond.append(func.to_tsvector(Notes.name_notes).bool_op("@@")(
                            func.phraseto_tsquery(search_text)))
        if search_by_text == 'on':
            cond.append(func.to_tsvector(Notes.text_notes).bool_op("@@")(
                            func.phraseto_tsquery(search_text)))
        q = select(func.count()).where(Notes.user_id == user_id)
        if search_text:
            q = q.where(or_(*cond))
        total_row = await database.execute(q)
        query = select(Notes).where(Notes.user_id == user_id)
        if search_text:
            query = query.where(or_(*cond))
        query = (
                query
                .order_by(desc(Notes.favourites == "on"))
                .order_by(desc(Notes.id))
                .limit(PAGE_SIZE)
                .offset(offset)
        )
        records = await database.fetch_all(query)
        data = []
        for record in records:
            note = Note.from_db(record, tz)
            # record.keywords = record.keywords.split(" ")
            data.append(note)
        response = {
            "total": total_row,
            "total_pages": math.ceil(total_row / PAGE_SIZE),
            "page": page_number,
            "page_size": PAGE_SIZE,
            "items": data
        }
        return response
    except SQLAlchemyError as error:
        logging.error("SQLAlchemyError", exc_info=True)
        return {"error": str(error)}


async def create_note_user(user_id, user_name, name_notes, text_notes):
    try:
        lang = langid.classify(text_notes)
        keywords = await parsing_text.extrack_keywords(text_notes)
        query = insert(Notes).values(
            user_id=user_id,
            username=user_name,
            name_notes=name_notes,
            text_notes=text_notes,
            favourites="off",
            date=datetime.now(),
            lang=lang[0],
            keywords=keywords,
        )
        return await database.execute(query)
    except SQLAlchemyError as error:
        logging.error("SQLAlchemyError", exc_info=True)
        return {"error": str(error)}


async def delete_note(user_id, note_id):
    try:
        query = (
            delete(Notes)
            .where(Notes.user_id == user_id)
            .where(Notes.id == note_id)
        )
        return await database.execute(query)
    except SQLAlchemyError as error:
        logging.error("SQLAlchemyError", exc_info=True)
        return {"error": str(error)}


async def create_note_file(user_id, note_id):
    try:
        new_file = uuid.uuid4()
        export_filepath = "temp/" + f"{new_file}.txt"
        q = (
            select(Notes)
            .where(Notes.id == note_id)
            .where(Notes.user_id == user_id)
        )
        res = await database.fetch_one(q)
        with open(export_filepath, "+a") as file:
            file.writelines(res.name_notes)
            file.writelines(res.text_notes)
        return export_filepath
    except SQLAlchemyError as error:
        logging.error("SQLAlchemyError", exc_info=True)
        return {"error": str(error)}


async def get_note_by_id(id, user_id):
    try:
        q = (
            select(Notes)
            .where(Notes.id == id)
            .where(Notes.user_id == user_id)
        )
        return await database.fetch_one(q)
    except SQLAlchemyError as error:
        logging.error("SQLAlchemyError", exc_info=True)
        return {"error": str(error)}


async def update_note_by_id(user_id, id, name_notes, text_notes):
    try:
        keywords = await parsing_text.extrack_keywords(text_notes)
        q = (
            update(Notes)
            .where(Notes.user_id == user_id)
            .where(Notes.id == id,)
            .values(
                name_notes=name_notes,
                text_notes=text_notes,
                keywords=keywords,
            )
        )
        await database.execute(q)
        query = (
            select(Notes)
            .where(Notes.user_id == user_id)
            .where(Notes.id == id)
        )
        return await database.fetch_one(query)
    except SQLAlchemyError as error:
        logging.error("SQLAlchemyError", exc_info=True)
        return {"error": str(error)}


async def add_note_favour(user_id, id, add_favour):
    try:
        q = (
            update(Notes)
            .where(Notes.user_id == user_id)
            .where(Notes.id == id)
            .values(favourites=add_favour)
        )
        await database.execute(q)
        query = (
            select(Notes)
            .where(Notes.user_id == user_id)
            .where(Notes.id == id)
        )
        return await database.fetch_one(query)
    except SQLAlchemyError as error:
        logging.error("SQLAlchemyError", exc_info=True)
        return {"error": str(error)}


async def regeneration():
    try:
        query = select().where(Notes.keywords == None)
        records = await database.fetch_all(query)
        for record in records:
            keywords = await parsing_text.extrack_keywords(text=record.text_notes, lang=record.lang)
            q = (
                update(Notes)
                .where(Notes.id == record.id)
                .values(keywords=keywords)
            )
            await database.execute(q)
        return "Ok!"
    except SQLAlchemyError as error:
        logging.error("SQLAlchemyError", exc_info=True)
        return {"error": str(error)}


async def regeneration_lang():
    try:
        query = select().where(Notes.lang == None)
        records = await database.fetch_all(query)
        for record in records:
            lang = langid.classify(record.text_notes)
            q = (
                update(Notes)
                .where(Notes.id == record.id)
                .values(lang=lang[0])
            )
            await database.execute(q)
        return "Ok!"
    except SQLAlchemyError as error:
        logging.error("SQLAlchemyError", exc_info=True)
        return {"error": str(error)}
