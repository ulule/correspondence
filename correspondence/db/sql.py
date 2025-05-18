from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import (Delete, Select, Update, delete, exists, func,
                            select, text, update)

Insert = postgresql.Insert
insert = postgresql.insert

__all__ = [
    "Select",
    "select",
    "Update",
    "update",
    "Insert",
    "insert",
    "Delete",
    "delete",
    "func",
    "text",
    "exists",
]
