import sqlalchemy

metadata = sqlalchemy.MetaData()

notes_table = sqlalchemy.Table(
    "notes",
    metadata,
    sqlalchemy.Column(
        "id",
        sqlalchemy.Integer,
        primary_key=True,
        autoincrement=True
        ),
    sqlalchemy.Column(
        "user_id",
        sqlalchemy.Integer,
        ),
    sqlalchemy.Column("username", sqlalchemy.String(100)),
    sqlalchemy.Column("name_notes", sqlalchemy.String(100), index=True),
    sqlalchemy.Column("text_notes", sqlalchemy.String(), index=True),
    sqlalchemy.Column("favourites", sqlalchemy.String(), default="off"),
    sqlalchemy.Column("date", sqlalchemy.DateTime())
)
