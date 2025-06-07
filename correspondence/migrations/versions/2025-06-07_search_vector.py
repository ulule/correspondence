"""search vector

Revision ID: 1fea454012c8
Revises: 3ffe9763c112
Create Date: 2025-06-07 21:15:12.053187

"""

from alembic import op
from sqlalchemy_searchable import sync_trigger

# revision identifiers, used by Alembic.
revision = "1fea454012c8"
down_revision = "3ffe9763c112"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    sync_trigger(
        conn,
        "correspondence_user",
        "search_vector",
        ["first_name", "last_name", "email", "phone_number"],
    )


def downgrade() -> None:
    pass
