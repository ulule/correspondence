import time
from typing import Annotated

import phonenumbers
import structlog
from fastapi import (APIRouter, Depends, Form, HTTPException, Request,
                     Response, status)
from sqlalchemy.ext.asyncio import AsyncSession

from correspondence.conf import settings
from correspondence.db import deps
from correspondence.deps import get_automessage_by_id
from correspondence.models import AutoMessage
from correspondence.utils import parse_phonenumber

router = APIRouter(prefix="/automessage")


@router.post("/{automessage_id}")
async def automessage(
    request: Request,
    phone_number: Annotated[str, Form(alias="contact[phone]")],
    active_campaign_id: Annotated[str, Form(alias="contact[id]")],
    response: Response,
    first_name: Annotated[str | None, Form(alias="contact[first_name]")] = None,
    last_name: Annotated[str | None, Form(alias="contact[last_name]")] = None,
    email: Annotated[str | None, Form(alias="contact[email]")] = None,
    automessage: AutoMessage = Depends(get_automessage_by_id),
    asession: AsyncSession = Depends(deps.get_db_asession),
):
    if not phone_number:
        raise HTTPException(status_code=400, detail="no phone_number provided")

    phone_number_instance = parse_phonenumber(phone_number, settings.DEFAULT_COUNTRY)

    if phone_number_instance is None or not phonenumbers.is_valid_number(
        phone_number_instance
    ):
        raise HTTPException(
            status_code=400, detail=f"invalid phone_number: {phone_number}"
        )

    phone_number = (
        f"+{phone_number_instance.country_code}{phone_number_instance.national_number}"
    )

    start_time = time.time()
    country_code = phonenumbers.region_code_for_number(phone_number_instance)

    message = await automessage.send_message(
        asession,
        request.app.provider,
        phone_number=phone_number,
        defaults={
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "country": country_code,
            "active_campaign_id": active_campaign_id,
        },
    )
    duration = time.time() - start_time

    logger = structlog.get_logger()

    if message:
        logger.debug("message created", duration=duration, message_id=message.id)

        response.status_code = status.HTTP_201_CREATED
        return ""

    logger.debug(
        "no message created, automessage already sent in conversation",
        automessage_id=automessage.id,
        duration=duration,
    )

    return ""
