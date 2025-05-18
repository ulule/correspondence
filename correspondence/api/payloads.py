from pydantic import BaseModel, EmailStr
from pydantic_extra_types.country import CountryAlpha2
from pydantic_extra_types.phone_numbers import PhoneNumber


class MessageCreatePayload(BaseModel):
    body: str
    sender_id: int | None = None


class UserCreatePayload(BaseModel):
    email: EmailStr | None = None
    first_name: str | None = None
    last_name: str | None = None
    phone_number: PhoneNumber
    manager_id: int
    country: CountryAlpha2
    active_campaign_id: str | None = None


class UserUpdatePayload(BaseModel):
    email: EmailStr | None = None
    first_name: str | None = None
    last_name: str | None = None
    phone_number: PhoneNumber | None = None
    manager_id: int | None = None
    country: CountryAlpha2 | None = None
    active_campaign_id: str | None = None
