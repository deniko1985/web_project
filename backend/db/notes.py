from datetime import datetime
import pytz
import uuid
from sqlalchemy import desc, func, or_, select, insert, delete, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
import math
import py3langid as langid
import logging
import json

from models.notes import Notes
# from models.dbs import db
from schemas.notes import GetNotes, AddNotes, UserNotesBase
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
        # note = (GetNotes(*record)).dict()
        date = record.date.astimezone(pytz.timezone(tz))
        record.date = date.strftime("%d-%m-%Y %H:%M")
        return record


async def get_all_notes(
        db: AsyncSession,
        user_id: int,
        tz: str,
        page_number: int,
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
        res = await db.execute(q)
        total_row = res.scalar()
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
        records = await db.execute(query)
        data = []
        for record in records.scalars().all():
            _ = {}
            note = Note.from_db(record, tz)
            # print("vars: ", vars(note))
            _["id"] = note.id
            _["name_notes"] = note.name_notes
            _["text_notes"] = note.text_notes
            _["lang"] = note.lang
            _["date"] = note.date
            data.append(_)
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


async def create_note_user(db: AsyncSession, user_id, user_name, name_notes, text_notes):
    try:
        lang = langid.classify(text_notes)
        keywords = await parsing_text.extrack_keywords(text_notes, lang)
        query = insert(Notes).values(
            user_id=user_id,
            username=user_name,
            name_notes=name_notes,
            text_notes=text_notes,
            favourites="off",
            date=datetime.now(),
            lang=lang[0],
            keywords=keywords,
        ).returning(Notes.id)
        records = await db.execute(query)
        await db.commit()
        return records.scalar()
    except SQLAlchemyError as error:
        logging.error("SQLAlchemyError", exc_info=True)
        return {"error": str(error)}


async def delete_note(db: AsyncSession, user_id: int, note_id: int):
    try:
        query = (
            delete(Notes)
            .where(Notes.user_id == user_id)
            .where(Notes.id == note_id)
        )
        result = await db.execute(query)
        await db.commit()
        return None
    except SQLAlchemyError as error:
        logging.error("SQLAlchemyError", exc_info=True)
        return {"error": str(error)}


async def create_note_file(db: AsyncSession, user_id: int, note_id: int):
    try:
        new_file = uuid.uuid4()
        export_filepath = "temp/" + f"{new_file}.txt"
        q = (
            select(Notes)
            .where(Notes.id == note_id)
            .where(Notes.user_id == user_id)
        )
        res = await db.execute(q)
        r = res.scalar()
        with open(export_filepath, "+a") as file:
            file.writelines(r.name_notes)
            file.writelines(r.text_notes)
        return export_filepath
    except SQLAlchemyError as error:
        logging.error("SQLAlchemyError", exc_info=True)
        return {"error": str(error)}


async def get_note_by_id(db: AsyncSession, id, user_id):
    try:
        query = (
            select(Notes)
            .where(Notes.id == id)
            .where(Notes.user_id == user_id)
        )
        result = await db.execute(query)
        return result.scalar()
    except SQLAlchemyError as error:
        logging.error("SQLAlchemyError", exc_info=True)
        return {"error": str(error)}


async def update_note_by_id(
        db: AsyncSession,
        user_id: int,
        id: int,
        name_notes: str,
        text_notes: str,
        lang: str,):
    try:
        keywords = await parsing_text.extrack_keywords(text_notes, lang)
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
        await db.execute(q)
        await db.commit()
        query = (
            select(Notes)
            .where(Notes.user_id == user_id)
            .where(Notes.id == id)
        )
        result = await db.execute(query)
        return result.scalar()
    except SQLAlchemyError as error:
        logging.error("SQLAlchemyError", exc_info=True)
        return {"error": str(error)}


async def add_note_favour(db: AsyncSession, user_id: int, id: int, add_favour: str):
    try:
        q = (
            update(Notes)
            .where(Notes.user_id == user_id)
            .where(Notes.id == id)
            .values(favourites=add_favour)
        )
        await db.execute(q)
        query = (
            select(Notes)
            .where(Notes.user_id == user_id)
            .where(Notes.id == id)
        )
        result = await db.execute(query)
        return result.scalar()
    except SQLAlchemyError as error:
        logging.error("SQLAlchemyError", exc_info=True)
        return {"error": str(error)}


async def regeneration(db: AsyncSession):
    try:
        query = select().where(Notes.keywords == None)
        records = await db.execute(query)
        for record in records:
            keywords = await parsing_text.extrack_keywords(text=record.text_notes, lang=record.lang)
            q = (
                update(Notes)
                .where(Notes.id == record.id)
                .values(keywords=keywords)
            )
            await db.execute(q)
        return "Ok!"
    except SQLAlchemyError as error:
        logging.error("SQLAlchemyError", exc_info=True)
        return {"error": str(error)}


async def regeneration_lang(db: AsyncSession):
    try:
        query = select().where(Notes.lang == None)
        records = await db.execute(query)
        for record in records:
            lang = langid.classify(record.text_notes)
            q = (
                update(Notes)
                .where(Notes.id == record.id)
                .values(lang=lang[0])
            )
            await db.execute(q)
        return "Ok!"
    except SQLAlchemyError as error:
        logging.error("SQLAlchemyError", exc_info=True)
        return {"error": str(error)}
