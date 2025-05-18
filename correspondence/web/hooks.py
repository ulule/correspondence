from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import ColumnElement

from correspondence.db.deps import get_db_asession
from correspondence.models import MessagePart, Organization
from correspondence.resources import MessageResource

router = APIRouter(prefix="/hooks")


class NexmoPayload(BaseModel):
    msisdn: str
    to: str
    message_id: Annotated[str, Field(alias="messageId")]
    concat: Annotated[str | None, Field(alias="concat-ref")] = None
    concat_ref: Annotated[str | None, Field(alias="concat-ref")] = None
    concat_part: Annotated[int | None, Field(alias="concat-part")] = None
    concat_total: Annotated[int | None, Field(alias="concat-total")] = None
    text: Annotated[str, Field(alias="text")]


@router.post("/nexmo")
async def nexmo(
    request: Request,
    payload: NexmoPayload,
    asession: AsyncSession = Depends(get_db_asession),
):
    phone_numbers = {"from": payload.msisdn, "to": payload.to}
    for k, v in phone_numbers.items():
        if v.startswith("+"):
            continue

        phone_numbers[k] = f"+{v}"

    organization = await Organization.get_from_phone_number(
        asession, phone_numbers["to"]
    )
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"organization with phone_number {phone_numbers['to']} does not exist",
        )

    user = await organization.get_user_from_phone_number(
        asession, phone_numbers["from"]
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"user with phone number {phone_numbers['from']} does not exist",
        )

    if not payload.concat:
        message = await user.create_message(
            asession,
            payload.text,
            send=False,
            extra_data={"provider_ids": [payload.message_id]},
        )

        return MessageResource.from_model(message)

    if not all([payload.concat_part is not None, payload.concat_ref is not None]):
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="payload is malformed",
        )

    repo = MessagePart.repository(asession)
    messagepart, created = await repo.aget_or_create(
        sender_id=user.id,
        provider_id=payload.message_id,
        defaults={
            "body": payload.text,
            "organization_id": organization.id,
            "part_id": payload.concat_part,
            "part_ref": payload.concat_ref,
        },
    )

    clauses: list[ColumnElement[bool]] = [
        MessagePart.organization_id == organization.id,
        MessagePart.part_ref == payload.concat_ref,
        MessagePart.message_id.is_(None),
    ]
    parts = await repo.aall(clauses=clauses)

    if len(parts) == payload.concat_total:
        parts = sorted(parts, key=lambda part: part.part_id)

        provider_ids = [part.provider_id for part in parts]

        body = "".join([part.body for part in parts])

        async with asession.begin_nested():
            message = await user.create_message(
                asession,
                body,
                send=False,
                extra_data={"provider_ids": provider_ids},
            )

            await asession.flush()
            await repo.abulk_update(clauses=clauses, message_id=message.id)

            return MessageResource.from_model(message)

    return {"message": "ok"}
