from fastapi import Depends

from correspondence.db.deps import get_db_asession
from correspondence.db.engine import AsyncSession
from correspondence.models import Conversation, Organization, User


async def get_organization_by_slug(
    organization_slug: str, asession: AsyncSession = Depends(get_db_asession)
) -> Organization:
    return await Organization.aget_by_or_404(slug=organization_slug, asession=asession)


async def get_organization_by_id(
    organization_id: int, asession: AsyncSession = Depends(get_db_asession)
) -> Organization:
    return await Organization.aget_or_404(organization_id, asession=asession)


async def get_conversation_by_id(
    conversation_id: int, asession: AsyncSession = Depends(get_db_asession)
) -> Conversation:
    return await Conversation.aget_or_404(conversation_id, asession=asession)


async def get_user_by_id(
    user_id: int, asession: AsyncSession = Depends(get_db_asession)
) -> User:
    return await User.aget_or_404(user_id, asession=asession)
