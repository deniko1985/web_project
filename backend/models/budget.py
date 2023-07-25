import sqlalchemy

metadata = sqlalchemy.MetaData()

budget_table = sqlalchemy.Table(
    "budget",
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
    sqlalchemy.Column("income", sqlalchemy.Float),
    sqlalchemy.Column("expense", sqlalchemy.Float),
    sqlalchemy.Column("comment", sqlalchemy.String()),
    sqlalchemy.Column("date", sqlalchemy.DateTime())
)
