from fastapi import APIRouter, Depends

from correspondence.api import deps
from correspondence.models import Conversation, Organization, User

router = APIRouter(prefix="/api")


@router.get("/users/")
async def user_list():
    return {"message": "ok"}


@router.get("/organizations/{organization_slug}/conversations/")
async def organization_conversation_list(
    organization: Organization = Depends(deps.get_organization_by_slug),
):
    return {"message": "ok"}


@router.get("/conversations/{conversation_id}/messages/")
async def conversation_message_list(
    conversation: Conversation = Depends(deps.get_conversation_by_id),
):
    return {"message": "ok"}


@router.get("/users/{user_id}/conversation")
async def user_conversation_detail(
    user: User = Depends(deps.get_user_by_id),
):
    conversation = await user.awaitable_attrs.conversation
    breakpoint()
    return {"message": "ok"}
