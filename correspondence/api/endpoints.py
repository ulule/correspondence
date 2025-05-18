from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from correspondence import auth, deps, resources
from correspondence.api import payloads
from correspondence.models import Conversation, Organization, User
from correspondence.pagination import PageResource, QueryPaginationParams
from correspondence.service import (ConversationAction, conversation_service,
                                    user_service)
from correspondence.utils import utc_now

router = APIRouter(prefix="/api")


@router.get("/users/")
async def user_list(
    pagination_params: Annotated[QueryPaginationParams, Query()],
    asession: AsyncSession = Depends(deps.get_db_asession),
    authenticated_user: User = Depends(auth.get_authenticated_user),
) -> PageResource[resources.UserResource]:
    items, total = await User.paginate(asession, pagination_params)
    return PageResource.from_results(
        pagination_params,
        [resources.UserResource.from_model(item) for item in items],
        total,
    )


@router.post(
    "/organizations/{organization_slug}/users/", status_code=status.HTTP_201_CREATED
)
async def organization_user_create(
    payload: payloads.UserCreatePayload,
    authenticated_user: User = Depends(auth.get_authenticated_user),
    asession: AsyncSession = Depends(deps.get_db_asession),
    organization: Organization = Depends(deps.get_organization_by_slug),
) -> resources.UserResource:
    user = await user_service.create(asession, organization, payload)

    return resources.UserResource.from_model(user)


@router.patch("/users/{user_id}/")
async def user_update(
    payload: payloads.UserUpdatePayload,
    authenticated_user: User = Depends(auth.get_authenticated_user),
    asession: AsyncSession = Depends(deps.get_db_asession),
    user: User = Depends(deps.get_user_by_id),
) -> resources.UserResource:
    user = await user_service.update(asession, user, payload)

    return resources.UserResource.from_model(user)


@router.get("/organizations/{organization_slug}/conversations/")
async def organization_conversation_list(
    pagination_params: Annotated[QueryPaginationParams, Query()],
    authenticated_user: User = Depends(auth.get_authenticated_user),
    asession: AsyncSession = Depends(deps.get_db_asession),
    organization: Organization = Depends(deps.get_organization_by_slug),
) -> PageResource[resources.ConversationResource]:
    manager = None
    if pagination_params.manager_id:
        manager = await User.repository(asession).aget_or_404(
            pagination_params.manager_id
        )

    items, total = await organization.get_conversations(
        asession, pagination_params, manager=manager
    )
    return PageResource.from_results(
        pagination_params,
        [
            resources.ConversationResource.from_model(
                item, extra_fields=["receiver", "last_message"]
            )
            for item in items
        ],
        total,
    )


@router.get("/conversations/{conversation_id}/messages/")
async def conversation_message_list(
    pagination_params: Annotated[QueryPaginationParams, Query()],
    authenticated_user: User = Depends(auth.get_authenticated_user),
    asession: AsyncSession = Depends(deps.get_db_asession),
    conversation: Conversation = Depends(deps.get_conversation_by_id),
) -> PageResource[resources.MessageResource]:
    items, total = await conversation.get_messages(asession, pagination_params)
    return PageResource.from_results(
        pagination_params,
        [
            resources.MessageResource.from_model(
                item,
                extra_fields=[
                    "conversation",
                    "conversation.receiver",
                    "conversation.receiver.manager",
                ],
            )
            for item in items
        ],
        total,
    )


@router.get("/users/{user_id}/conversation/")
async def user_conversation_detail(
    user: User = Depends(deps.get_user_by_id),
    authenticated_user: User = Depends(auth.get_authenticated_user),
    asession: AsyncSession = Depends(deps.get_db_asession),
) -> resources.ConversationResource:
    conversation = await user.get_conversation(asession)
    if not conversation:
        conversation = Conversation(
            receiver=user,
            unread=False,
            created_at=utc_now(),
            messages_count=0,
            id=0,
        )

    if conversation.unread:
        await conversation_service.mark_as(
            asession, conversation, ConversationAction.read
        )

    return resources.ConversationResource.from_model(
        conversation, extra_fields=["receiver", "receiver.manager", "last_message"]
    )


@router.post("/users/{user_id}/conversation/", status_code=status.HTTP_201_CREATED)
async def user_conversation_create(
    payload: payloads.MessageCreatePayload,
    request: Request,
    user: User = Depends(deps.get_user_by_id),
    authenticated_user: User = Depends(auth.get_authenticated_user),
    asession: AsyncSession = Depends(deps.get_db_asession),
) -> resources.MessageResource:
    sender = authenticated_user
    if payload.sender_id:
        sender = await User.repository(asession).aget_or_404(payload.sender_id)

    message = await user_service.create_message(
        asession, request.app.provider, sender, user, payload
    )

    return resources.MessageResource.from_model(
        message,
        extra_fields=[
            "conversation",
            "conversation.receiver",
            "conversation.last_message",
            "conversation.receiver.manager",
        ],
    )


@router.post("/conversations/{conversation_id}/{action}/")
async def conversation_action(
    action: ConversationAction,
    authenticated_user: User = Depends(auth.get_authenticated_user),
    conversation: Conversation = Depends(deps.get_conversation_by_id),
    asession: AsyncSession = Depends(deps.get_db_asession),
) -> resources.ConversationResource:
    conversation = await conversation_service.mark_as(asession, conversation, action)

    return resources.ConversationResource.from_model(conversation)
