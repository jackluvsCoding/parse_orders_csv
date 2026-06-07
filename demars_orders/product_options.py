"""Helpers for parsing Weebly product options.

Weebly stores several customer selections inside one long text field named
`Product Options`. This module extracts the useful pieces into separate values
that can be used by the workbook, OptimoRoute import, and review checks.
"""

import re
from typing import Tuple

from demars_orders.constants import PRODUCT_OPTION_LABELS
from demars_orders.text_utils import clean_text


def extract_product_option(options_text: str, option_label: str) -> str:
    """Extract a named option value from Weebly's combined `Product Options` text.

    Weebly does not export each product option as its own column. Instead, values
    come through as one string, for example:

        Pickup/Drop Site : GRIND NOLO (Friday), Preferences : No kale

    The parser looks for the requested label and captures everything until the
    next known label or the end of the string.
    """
    next_labels = "|".join(re.escape(label) for label in PRODUCT_OPTION_LABELS if label != option_label)
    pattern = rf"{re.escape(option_label)}\s*:\s*(.*?)(?=,\s*(?:{next_labels})\s*:|$)"
    match = re.search(pattern, options_text or "", flags=re.IGNORECASE | re.DOTALL)
    return clean_text(match.group(1)) if match else ""


def split_site_name_and_address(pickup_drop_site: str) -> Tuple[str, str]:
    """Split a pickup/drop-site option into display name and route address.

    Many seasonal pickup/drop-site options are formatted like:

        GRIND NOLO - 515 N Washington Ave, Minneapolis, MN 55401 (Friday)

    This function removes the trailing day-of-week note, then treats the last
    ` - ` section as an address when it contains a number.

    Returns:
        (site_name, site_address)
    """
    site = clean_text(pickup_drop_site)
    if not site:
        return "", ""

    # Remove a trailing parenthetical such as "(Friday)" or "(Sunday PM)".
    site_without_day = re.sub(r"\s*\([^)]*\)\s*$", "", site).strip()
    pieces = [part.strip() for part in site_without_day.split(" - ") if part.strip()]

    # If the final section has a number, it is probably a street address.
    if len(pieces) >= 2 and re.search(r"\d", pieces[-1]):
        return " - ".join(pieces[:-1]), pieces[-1]

    return site_without_day, ""
