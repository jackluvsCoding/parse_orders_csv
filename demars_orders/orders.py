"""Build the clean one-row-per-order dataset from a raw Weebly export.

This is the heart of the processor. The raw Weebly CSV can include multiple rows
per order: one row with customer/order data and one or more rows with product
data. This module groups rows by `Order #`, keeps the important order/customer
fields, parses product option details, and produces a normalized DataFrame.
"""

import re
from typing import Dict, List

import pandas as pd

from demars_orders.constants import (
    ALLERGIES_OPTION,
    DELIVERY_ADDRESS_OVERRIDE_OPTION,
    FULFILLMENT_CATEGORY_DELIVERY,
    FULFILLMENT_CATEGORY_DROP_SITE,
    IGNORED_DELIVERY_OVERRIDE_VALUES,
    ORDER_DATE_COLUMN,
    ORDER_NOTES_COLUMN,
    ORDER_NUMBER_COLUMN,
    ORDER_STATUS_COLUMN,
    PICKUP_DROP_SITE_OPTION,
    PREFERENCES_OPTION,
    PRODUCT_ID_COLUMN,
    PRODUCT_NAME_COLUMN,
    PRODUCT_OPTIONS_COLUMN,
    PRODUCT_QUANTITY_COLUMN,
    SHIPPING_ADDRESS_1_COLUMN,
    SHIPPING_ADDRESS_2_COLUMN,
    SHIPPING_CITY_COLUMN,
    SHIPPING_COUNTRY_COLUMN,
    SHIPPING_EMAIL_COLUMN,
    SHIPPING_FIRST_NAME_COLUMN,
    SHIPPING_LAST_NAME_COLUMN,
    SHIPPING_PHONE_COLUMN,
    SHIPPING_POSTAL_CODE_COLUMN,
    SHIPPING_REGION_COLUMN,
)
from demars_orders.fulfillment import determine_fulfillment
from demars_orders.product_options import extract_product_option
from demars_orders.text_utils import clean_text, first_non_empty_value, format_full_address


def parse_share_size(product_name: str) -> str:
    """Return `Full` or `Half` from the product name when possible."""
    name = clean_text(product_name).lower()

    if name.startswith("full"):
        return "Full"

    if name.startswith("half"):
        return "Half"

    return ""


def build_product_string(products: List[Dict[str, str]]) -> str:
    """Create a compact audit string for the `All Orders - Clean` tab.

    This keeps the original product details visible in the full clean tab while
    the working tabs stay simpler. It mirrors the old script's general output so
    the generated workbook remains easy to compare against prior seasons.
    """
    product_strings = []

    for product in products:
        product_strings.append(str({
            "id": product.get("product_id", ""),
            "product": product.get("product_name", ""),
            "quantity": product.get("quantity", ""),
            "Product Options": product.get("product_options", ""),
        }))

    return "".join(product_strings)


def should_use_delivery_override(delivery_override: str) -> bool:
    """Return whether a free-text delivery override is usable as an address.

    Customers sometimes type values like `same`, `N/A`, `Roseville`, or partial
    addresses into the delivery override field. Those should not replace the
    cleaner Weebly shipping address. This helper is intentionally conservative.
    """
    override = clean_text(delivery_override).lower()

    if not override or override in IGNORED_DELIVERY_OVERRIDE_VALUES:
        return False

    # Require at least one digit and enough text to look address-like.
    return bool(re.search(r"\d", override) and len(override) >= 8)


def build_order_notes(share_size: str, order_notes: str) -> str:
    """Build the single notes value used across working tabs and OptimoRoute.

    The farm workflow wants the notes column to start with the share size, then
    include customer-provided order notes when they exist.

    Examples:
        Half: Please leave by side door
        Full:
    """
    share = clean_text(share_size)
    notes = clean_text(order_notes)

    if share and notes:
        return f"{share}: {notes}"

    if share:
        return f"{share}:"

    return notes


def choose_delivery_route_address(customer_address: str, delivery_override: str) -> str:
    """Choose the address used for routing a delivery order.

    The Weebly shipping address is usually cleaner than the customer-entered
    delivery override. Use the override only when the shipping address is blank
    and the override looks address-like.
    """
    customer_address = clean_text(customer_address)
    delivery_override = clean_text(delivery_override)

    if customer_address:
        return customer_address

    if should_use_delivery_override(delivery_override):
        return delivery_override.replace("\n", ", ")

    return ""


def build_clean_orders_dataframe(raw_orders_df: pd.DataFrame) -> pd.DataFrame:
    """Convert the raw Weebly export into one clean row per order.

    Args:
        raw_orders_df: DataFrame created from the Weebly orders CSV export.

    Returns:
        A normalized DataFrame where each row represents one CSA order and
        includes both source/audit fields and derived workflow fields.
    """
    raw_orders_df = raw_orders_df.copy().fillna("")
    clean_order_records = []

    # Grouping by Order # is what collapses Weebly's multi-row-per-order export
    # into the one-row-per-order structure needed for the farm workflow.
    for order_number, order_group in raw_orders_df.groupby(ORDER_NUMBER_COLUMN, sort=False):
        order_group = order_group.fillna("")

        # Product rows are the rows where Product Id is populated. Most customer
        # fields are blank on those rows, so we collect them separately.
        product_rows = order_group[order_group[PRODUCT_ID_COLUMN].astype(str).str.strip() != ""]
        products = []

        for _, product_row in product_rows.iterrows():
            products.append({
                "product_id": clean_text(product_row.get(PRODUCT_ID_COLUMN, "")),
                "product_name": clean_text(product_row.get(PRODUCT_NAME_COLUMN, "")),
                "product_options": clean_text(product_row.get(PRODUCT_OPTIONS_COLUMN, "")),
                "quantity": clean_text(product_row.get(PRODUCT_QUANTITY_COLUMN, "")),
            })

        # Most orders have exactly one CSA product. If an order has more than one
        # product, the first product drives the routing fields and the full
        # product string remains visible in `All Orders - Clean` for audit.
        primary_product = products[0] if products else {
            "product_id": "",
            "product_name": "",
            "product_options": "",
            "quantity": "",
        }

        product_options = primary_product.get("product_options", "")
        pickup_drop_site = extract_product_option(product_options, PICKUP_DROP_SITE_OPTION)
        delivery_override = extract_product_option(product_options, DELIVERY_ADDRESS_OVERRIDE_OPTION)
        allergies = extract_product_option(product_options, ALLERGIES_OPTION)
        preferences = extract_product_option(product_options, PREFERENCES_OPTION)

        fulfillment, fulfillment_category, site_name, site_address = determine_fulfillment(
            primary_product.get("product_name", ""),
            pickup_drop_site,
        )

        address_1 = first_non_empty_value(order_group[SHIPPING_ADDRESS_1_COLUMN])
        address_2 = first_non_empty_value(order_group[SHIPPING_ADDRESS_2_COLUMN])
        city = first_non_empty_value(order_group[SHIPPING_CITY_COLUMN])
        state = first_non_empty_value(order_group[SHIPPING_REGION_COLUMN])
        postal_code = first_non_empty_value(order_group[SHIPPING_POSTAL_CODE_COLUMN])
        customer_address = format_full_address(address_1, address_2, city, state, postal_code)

        # OptimoRoute needs a single route address. Deliveries use the customer
        # shipping address. Drop sites use the route address parsed from the
        # pickup/drop-site option. Pickups keep the customer address for reference.
        if fulfillment_category == FULFILLMENT_CATEGORY_DROP_SITE:
            optimo_address = site_address
        elif fulfillment_category == FULFILLMENT_CATEGORY_DELIVERY:
            optimo_address = choose_delivery_route_address(customer_address, delivery_override)
        else:
            optimo_address = customer_address

        first_name = first_non_empty_value(order_group[SHIPPING_FIRST_NAME_COLUMN])
        last_name = first_non_empty_value(order_group[SHIPPING_LAST_NAME_COLUMN])
        share_size = parse_share_size(primary_product.get("product_name", ""))
        raw_order_notes = first_non_empty_value(order_group[ORDER_NOTES_COLUMN])

        clean_order_records.append({
            # Source/audit fields from Weebly.
            "order_number": clean_text(order_number),
            "date": first_non_empty_value(order_group[ORDER_DATE_COLUMN]),
            "status": first_non_empty_value(order_group[ORDER_STATUS_COLUMN]),
            "first_name": first_name,
            "last_name": last_name,
            "email": first_non_empty_value(order_group[SHIPPING_EMAIL_COLUMN]),
            "address_1": address_1,
            "address_2": address_2,
            "postal_code": postal_code,
            "city": city,
            "state": state,
            "country": first_non_empty_value(order_group[SHIPPING_COUNTRY_COLUMN]),
            "phone": first_non_empty_value(order_group[SHIPPING_PHONE_COLUMN]),
            "products": build_product_string(products),
            "product_options": product_options,
            "order_notes": raw_order_notes,

            # Derived fields that make the workbook easier to use.
            "location_name": " ".join(part for part in [first_name, last_name] if part),
            "address": customer_address,
            "product_id": primary_product.get("product_id", ""),
            "product_name": primary_product.get("product_name", ""),
            "quantity": primary_product.get("quantity", ""),
            "share_size": share_size,
            "pickup_drop_site": pickup_drop_site,
            "delivery_address_override": delivery_override,
            "allergies": allergies,
            "preferences": preferences,
            "fulfillment": fulfillment,
            "fulfillment_category": fulfillment_category,
            "site_name": site_name,
            "site_address": site_address,
            "optimo_address": optimo_address,
            "notes": build_order_notes(share_size, raw_order_notes),
        })

    return pd.DataFrame(clean_order_records)
