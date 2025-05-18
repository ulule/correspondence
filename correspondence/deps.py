from fastapi import Depends
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.strategy_options import selectinload

from correspondence.db.deps import get_db_asession
from correspondence.db.engine import AsyncSession
from correspondence.models import AutoMessage, Conversation, Organization, User


async def get_organization_by_slug(
    organization_slug: str, asession: AsyncSession = Depends(get_db_asession)
) -> Organization:
    return await Organization.repository(asession).aget_by_or_404(
        filter_by={"slug": organization_slug},
        options=[selectinload(Organization.phone_numbers)],
    )


async def get_organization_by_id(
    organization_id: int, asession: AsyncSession = Depends(get_db_asession)
) -> Organization:
    return await Organization.repository(asession).aget_or_404(organization_id)


async def get_conversation_by_id(
    conversation_id: int, asession: AsyncSession = Depends(get_db_asession)
) -> Conversation:
    return await Conversation.repository(asession).aget_or_404(
        conversation_id,
        options=[
            joinedload(Conversation.receiver),
            joinedload(Conversation.last_message),
        ],
    )


async def get_user_by_id(
    user_id: int, asession: AsyncSession = Depends(get_db_asession)
) -> User:
    return await User.repository(asession).aget_or_404(
        user_id, options=[joinedload(User.manager)]
    )


async def get_automessage_by_id(
    automessage_id: int, asession: AsyncSession = Depends(get_db_asession)
) -> AutoMessage:
    return await AutoMessage.repository(asession).aget_or_404(automessage_id)
