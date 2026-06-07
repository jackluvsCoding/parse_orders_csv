"""Build the workbook-specific reporting DataFrames.

The clean orders DataFrame is intentionally complete and verbose. The functions
in this module reshape that full dataset into smaller purpose-built views:
working tabs, OptimoRoute import, review queue, and summary counts.
"""

from typing import List

import pandas as pd

from demars_orders.constants import (
    FULFILLMENT_CATEGORY_DELIVERY,
    FULFILLMENT_CATEGORY_DROP_SITE,
    FULFILLMENT_CATEGORY_PICKUP,
    FULFILLMENT_CATEGORY_UNKNOWN,
    IGNORED_DELIVERY_OVERRIDE_VALUES,
)
from demars_orders.text_utils import clean_text, normalize_for_compare


WORKING_TAB_COLUMNS: List[str] = [
    "location_name",
    "email",
    "phone",
    "address",
    "product_name",
    "fulfillment",
    "quantity",
    "allergies",
    "notes",
]


def build_working_orders_dataframe(clean_orders_df: pd.DataFrame) -> pd.DataFrame:
    """Return the lean view used for All Pickups/Deliveries/Drops tabs.

    These tabs are intended for day-to-day farm operations, so they exclude audit
    fields such as order number, date, status, country, and individual address
    columns. The full details remain available in `All Orders - Clean`.
    """
    return clean_orders_df.loc[:, WORKING_TAB_COLUMNS].copy()


def build_optimo_dataframe(clean_orders_df: pd.DataFrame) -> pd.DataFrame:
    """Return rows formatted for OptimoRoute import.

    Only delivery and drop-site rows are routable. True pickups are excluded
    because the customer comes to the farm/market/pickup location.
    """
    routable_orders = clean_orders_df[
        clean_orders_df["fulfillment_category"].isin([
            FULFILLMENT_CATEGORY_DELIVERY,
            FULFILLMENT_CATEGORY_DROP_SITE,
        ])
    ].copy()

    return pd.DataFrame({
        "Location": routable_orders["location_name"],
        "Address": routable_orders["optimo_address"],
        "email": routable_orders["email"],
        "phone": routable_orders["phone"],
        "fulfillment": routable_orders["fulfillment"],
        "notes": routable_orders["notes"],
    })


def build_review_needed_dataframe(clean_orders_df: pd.DataFrame) -> pd.DataFrame:
    """Return a human-review queue for suspicious or incomplete rows.

    The goal is not to block processing. The workbook should still generate.
    This tab simply highlights rows Jack/Jordan may want to review before route
    planning, such as missing contact data or drop sites without route addresses.
    """
    review_records = []

    for _, order in clean_orders_df.iterrows():
        issues = []

        if not order.get("email"):
            issues.append("Missing email")

        if not order.get("phone"):
            issues.append("Missing phone")

        if order.get("fulfillment_category") == FULFILLMENT_CATEGORY_UNKNOWN:
            issues.append("Unknown fulfillment - check product options")

        if order.get("fulfillment_category") == FULFILLMENT_CATEGORY_DELIVERY and not order.get("optimo_address"):
            issues.append("Delivery order missing route address")

        delivery_override = order.get("delivery_address_override", "")
        if delivery_override and clean_text(delivery_override).lower() not in IGNORED_DELIVERY_OVERRIDE_VALUES:
            customer_address = order.get("address", "")
            if normalize_for_compare(delivery_override) != normalize_for_compare(customer_address):
                issues.append(
                    "Delivery override present - using shipping address for Optimo: "
                    f"{delivery_override}"
                )

        if order.get("fulfillment_category") == FULFILLMENT_CATEGORY_DROP_SITE and not order.get("site_address"):
            issues.append("Drop site missing route address")

        if not order.get("share_size"):
            issues.append("Could not parse share size")

        if issues:
            review_records.append({
                "order_number": order.get("order_number", ""),
                "customer": order.get("location_name", ""),
                "fulfillment": order.get("fulfillment", ""),
                "issues": "; ".join(issues),
                "product_options": order.get("product_options", ""),
                "notes": order.get("notes", ""),
            })

    return pd.DataFrame(review_records)


def build_summary_dataframe(clean_orders_df: pd.DataFrame) -> pd.DataFrame:
    """Return order counts by fulfillment category, fulfillment, and share size."""
    return (
        clean_orders_df
        .groupby(["fulfillment_category", "fulfillment", "share_size"], dropna=False)
        .size()
        .reset_index(name="order_count")
        .sort_values(["fulfillment_category", "fulfillment", "share_size"])
    )


def split_orders_by_fulfillment_category(clean_orders_df: pd.DataFrame):
    """Return lean pickup, delivery, and drop-site DataFrames for workbook tabs."""
    pickups = build_working_orders_dataframe(
        clean_orders_df[clean_orders_df["fulfillment_category"] == FULFILLMENT_CATEGORY_PICKUP].copy()
    )
    deliveries = build_working_orders_dataframe(
        clean_orders_df[clean_orders_df["fulfillment_category"] == FULFILLMENT_CATEGORY_DELIVERY].copy()
    )
    drops = build_working_orders_dataframe(
        clean_orders_df[clean_orders_df["fulfillment_category"] == FULFILLMENT_CATEGORY_DROP_SITE].copy()
    )

    return pickups, deliveries, drops
