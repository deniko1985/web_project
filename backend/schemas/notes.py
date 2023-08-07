from pydantic import BaseModel
from pydantic.typing import Optional
from datetime import datetime


class UserNotesBase(BaseModel):
    id: int
    user_id: int
    username: str
    name_notes: str
    text_notes: str
    favourites: str
    date: datetime
    keywords: list


class AddNotes(BaseModel):
    user_id: int
    username: str
    name_notes: str
    text_notes: str
    favourites: str
    date: datetime
    keywords: list


class UserNote(BaseModel):
    id: int


class UpdateNote(BaseModel):
    id: int
    name_notes: str
    text_notes: str


class SearchNotes(BaseModel):
    id: int
    name_notes: str
    text_notes: str
    date: datetime


class GetNotes(BaseModel):
    id: int
    name_notes: str
    text_notes: str
    favourites: Optional[str]
    date: datetime
