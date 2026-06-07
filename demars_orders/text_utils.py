"""Small text-cleaning helpers.

The Weebly CSV export contains many fields that are blank, numeric-looking,
or typed free-form by customers. These helpers make the rest of the code easier
to read by centralizing common cleanup rules.
"""

import re
from typing import Any


def clean_text(value: Any) -> str:
    """Return a consistently cleaned string value.

    Why this exists:
    - pandas can read blank cells as NaN unless told otherwise.
    - Spreadsheet-style numeric IDs sometimes show up as `123.0`.
    - Customer-entered fields often include accidental leading/trailing spaces.
    """
    if value is None:
        return ""

    text = str(value).strip()

    if text.lower() in {"nan", "none"}:
        return ""

    # If a value like an order number or phone number is read as `12345.0`,
    # remove the artificial decimal portion.
    if text.endswith(".0") and text[:-2].isdigit():
        return text[:-2]

    return text


def first_non_empty_value(series) -> str:
    """Return the first meaningful value from a pandas Series-like object.

    Weebly exports each order across multiple rows. Usually the customer data is
    on one row and product data is on another. Grouping by `Order #` lets us scan
    the group and keep the first populated value for each customer/order field.
    """
    for value in series:
        text = clean_text(value)
        if text:
            return text
    return ""


def format_full_address(address_1: str, address_2: str, city: str, state: str, postal_code: str) -> str:
    """Build a single human-readable address from the Weebly shipping fields."""
    street = ", ".join(part for part in [clean_text(address_1), clean_text(address_2)] if part)
    city_state = ", ".join(part for part in [clean_text(city), clean_text(state)] if part)
    city_state_zip = " ".join(part for part in [city_state, clean_text(postal_code)] if part)
    return ", ".join(part for part in [street, city_state_zip] if part)


def normalize_for_compare(value: str) -> str:
    """Normalize text so two address strings can be compared loosely.

    This is used only for validation/review checks. It intentionally removes
    spaces, punctuation, and casing so minor formatting differences do not create
    noisy review warnings.
    """
    return re.sub(r"[^a-z0-9]", "", clean_text(value).lower())
