"""Fulfillment classification logic.

This module decides whether an order is a home delivery, pickup, drop site, or
unknown. The output category determines which workbook tabs the order appears in
and whether it is included in the OptimoRoute import.

The matching rules are intentionally simple and readable because the farm's
pickup/drop-site options change by season. This file is a natural place to
update yearly fulfillment logic until the project adds a dedicated config file.
"""

from typing import Tuple

from demars_orders.constants import (
    FULFILLMENT_CATEGORY_DELIVERY,
    FULFILLMENT_CATEGORY_DROP_SITE,
    FULFILLMENT_CATEGORY_PICKUP,
    FULFILLMENT_CATEGORY_UNKNOWN,
)
from demars_orders.product_options import split_site_name_and_address
from demars_orders.text_utils import clean_text


def determine_fulfillment(product_name: str, pickup_drop_site: str) -> Tuple[str, str, str, str]:
    """Determine fulfillment display value, category, site name, and site address.

    Args:
        product_name: The Weebly product name, such as `Half-Share CSA - [PICKUP]`.
        pickup_drop_site: The parsed Pickup/Drop Site product option.

    Returns:
        A tuple of:
        - fulfillment: user-friendly value shown in workbook tabs
        - fulfillment_category: internal bucket used for filtering/routing
        - site_name: parsed pickup/drop-site name, if available
        - site_address: parsed route address for drop sites, if available
    """
    product = clean_text(product_name)
    site_name, site_address = split_site_name_and_address(pickup_drop_site)
    site_name_lower = site_name.lower()

    # Home delivery is indicated directly in the product name.
    # These rows are included in the OptimoRoute import.
    if "[delivery]" in product.lower():
        return "Delivery", FULFILLMENT_CATEGORY_DELIVERY, "", ""

    # If the product is not a delivery and we cannot parse a site, the order
    # needs a human review because we do not know where it belongs.
    if not site_name:
        return "Unknown", FULFILLMENT_CATEGORY_UNKNOWN, "", ""

    # True pickups are not included in OptimoRoute because the customer comes to
    # the farm/market/location rather than being routed by the driver.
    if "demars farms" in site_name_lower:
        return "Farm Pickup", FULFILLMENT_CATEGORY_PICKUP, site_name, site_address

    if "farmers market" in site_name_lower:
        return "Elk River Farmers Market", FULFILLMENT_CATEGORY_PICKUP, site_name, site_address

    # Drop sites are routed in OptimoRoute because produce is delivered to a
    # shared location for customer pickup.
    if "roseville" in site_name_lower:
        return "Roseville Drop", FULFILLMENT_CATEGORY_DROP_SITE, site_name, site_address

    if "grind" in site_name_lower:
        return f"{site_name} Drop", FULFILLMENT_CATEGORY_DROP_SITE, site_name, site_address

    if "connexus" in site_name_lower:
        return "Connexus Energy Ramsey Drop", FULFILLMENT_CATEGORY_DROP_SITE, site_name, site_address

    # Default new or unrecognized pickup/drop-site options to drop sites so they
    # appear in routing prep rather than disappearing from the workflow.
    # The Review Needed tab will flag rows that do not have a route address.
    return f"{site_name} Drop", FULFILLMENT_CATEGORY_DROP_SITE, site_name, site_address
