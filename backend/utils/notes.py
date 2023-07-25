from datetime import datetime
import pytz
import uuid
from sqlalchemy import desc, func, or_, select
import math
import py3langid as langid

from models.notes import notes_table as notes
from models.db import database
from schemas.notes import GetNotes


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
    PAGE_SIZE = 9
    offset = (page_number - 1) * PAGE_SIZE
    cond = []
    if search_by_name == 'on':
        cond.append(func.to_tsvector(notes.c.name_notes).bool_op("@@")(
                        func.phraseto_tsquery(search_text)))
    if search_by_text == 'on':
        cond.append(func.to_tsvector(notes.c.text_notes).bool_op("@@")(
                        func.phraseto_tsquery(search_text)))
    q = select(func.count()).where(notes.c.user_id == user_id)
    if search_text:
        q = q.where(or_(*cond))
    total_row = await database.execute(q)
    query = notes.select().where(notes.c.user_id == user_id)
    if search_text:
        query = query.where(or_(*cond))
    query = (
            query
            .order_by(desc(notes.c.favourites == "on"))
            .order_by(desc(notes.c.id))
            .limit(PAGE_SIZE)
            .offset(offset)
            )
    records = await database.fetch_all(query)
    data = []
    for record in records:
        note = Note.from_db(record, tz)
        data.append(note)
    response = {
        "total": total_row,
        "total_pages": math.ceil(total_row / PAGE_SIZE),
        "page": page_number,
        "page_size": PAGE_SIZE,
        "items": data
    }
    return response


async def create_note_user(user_id, user_name, name_notes, text_notes):
    lang = langid.classify(text_notes)
    query = notes.insert().values(
        user_id=user_id,
        username=user_name,
        name_notes=name_notes,
        text_notes=text_notes,
        favourites="off",
        date=datetime.now(),
        lang=lang[0]
        )
    return await database.execute(query)


async def delete_note(user_id, note_id):
    query = (
        notes.delete()
        .where(notes.c.user_id == user_id)
        .where(notes.c.id == note_id)
        )
    return await database.execute(query)


async def create_note_file(user_id, note_id):
    new_file = uuid.uuid4()
    export_filepath = "temp/" + f"{new_file}.txt"
    q = (
        notes.select()
        .where(notes.c.id == note_id)
        .where(notes.c.user_id == user_id)
        )
    res = await database.fetch_one(q)
    with open(export_filepath, "+a") as file:
        file.writelines(res.name_notes)
        file.writelines(res.text_notes)
    return export_filepath


async def get_note_by_id(id, user_id):
    q = (
        notes.select()
        .where(notes.c.id == id)
        .where(notes.c.user_id == user_id)
        )
    return await database.fetch_one(q)


async def update_note_by_id(user_id, id, name_notes, text_notes):
    q = (
        notes.update()
        .where(notes.c.user_id == user_id)
        .where(notes.c.id == id,)
        .values(
            name_notes=name_notes,
            text_notes=text_notes,
            )
        )
    await database.execute(q)
    query = (
        notes.select()
        .where(notes.c.user_id == user_id)
        .where(notes.c.id == id)
        )
    return await database.fetch_one(query)


async def add_note_favour(user_id, id, add_favour):
    q = (
        notes.update()
        .where(notes.c.user_id == user_id)
        .where(notes.c.id == id)
        .values(favourites=add_favour)
        )
    await database.execute(q)
    query = (
        notes.select()
        .where(notes.c.user_id == user_id)
        .where(notes.c.id == id)
        )
    return await database.fetch_one(query)
