from datetime import datetime, timezone
from functools import lru_cache

import phonenumbers
from phonenumbers.phonenumberutil import NumberParseException
from sqlalchemy_utils import i18n

utc = timezone.utc


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@lru_cache(maxsize=None)
def get_countries() -> list[tuple[str, str]]:
    locale = i18n.get_locale()

    country_codes = filter(lambda item: len(item) == 2, locale.territories.keys())

    return sorted(
        [
            (country_code, locale.territories[country_code])
            for country_code in country_codes
        ],
        key=lambda entry: entry[1],
    )


def parse_phonenumber(
    phone_number: str, default_country: str
) -> phonenumbers.PhoneNumber | None:
    for country in (None, default_country):
        try:
            phone_number_instance = phonenumbers.parse(phone_number, country)
        except NumberParseException:
            pass
        else:
            return phone_number_instance

    return None


def import_string(path: str):
    """
    Path must be module.path.ClassName
    >>> cls = import_string('sentry.models.Group')
    """
    if "." not in path:
        return __import__(path)

    module_name, class_name = path.rsplit(".", 1)

    module = __import__(module_name, {}, {}, [class_name])
    try:
        return getattr(module, class_name)

    except AttributeError as exc:
        raise ImportError from exc
