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


class AddNotes(BaseModel):
    name_notes: str
    text_notes: str


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
