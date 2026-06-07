import csv
import re
from pathlib import Path
from typing import Any, Optional

import pandas as pd

from file_io import asksaveasfile_csv_wrapper, asksaveasfile_xlsx_wrapper


def _clean(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if text.lower() in {"nan", "none"}:
        return ""
    if text.endswith(".0") and text[:-2].isdigit():
        return text[:-2]
    return text


def _first_non_empty(series) -> str:
    for value in series:
        text = _clean(value)
        if text:
            return text
    return ""


def _format_address(address_1: str, address_2: str, city: str, state: str, postal_code: str) -> str:
    street = ", ".join(part for part in [_clean(address_1), _clean(address_2)] if part)
    city_state = ", ".join(part for part in [_clean(city), _clean(state)] if part)
    city_state_zip = " ".join(part for part in [city_state, _clean(postal_code)] if part)
    return ", ".join(part for part in [street, city_state_zip] if part)


def _extract_option(options: str, label: str) -> str:
    labels = [
        "Pickup/Drop Site",
        "Delivery Address (If different from billing)",
        "Allergies (We will do our best to accommodate allergies, but cannot guarantee produce is free of cross contamination)",
        "Preferences (We will do our best to accommodate preferences, but cannot guarantee replacement items)",
    ]
    next_labels = "|".join(re.escape(item) for item in labels if item != label)
    pattern = rf"{re.escape(label)}\s*:\s*(.*?)(?=,\s*(?:{next_labels})\s*:|$)"
    match = re.search(pattern, options or "", flags=re.IGNORECASE | re.DOTALL)
    return _clean(match.group(1)) if match else ""


def _share_size(product_name: str) -> str:
    name = _clean(product_name).lower()
    if name.startswith("full"):
        return "Full"
    if name.startswith("half"):
        return "Half"
    return ""


def _site_name_and_address(site: str):
    site = _clean(site)
    if not site:
        return "", ""

    site_without_day = re.sub(r"\s*\([^)]*\)\s*$", "", site).strip()
    pieces = [part.strip() for part in site_without_day.split(" - ") if part.strip()]

    # Many Weebly options are formatted as "Site Name - Street, City, ST ZIP".
    if len(pieces) >= 2 and re.search(r"\d", pieces[-1]):
        return " - ".join(pieces[:-1]), pieces[-1]

    return site_without_day, ""


def _fulfillment(product_name: str, pickup_site: str):
    product = _clean(product_name)
    site_name, site_address = _site_name_and_address(pickup_site)
    site_lower = site_name.lower()

    if "[delivery]" in product.lower():
        return "Delivery", "delivery", "", ""

    if not site_name:
        return "Unknown", "unknown", "", ""

    if "demars farms" in site_lower:
        return "Farm Pickup", "pickup", site_name, site_address
    if "farmers market" in site_lower:
        return "Elk River Farmers Market", "pickup", site_name, site_address
    if "roseville" in site_lower:
        return "Roseville Drop", "drop_site", site_name, site_address
    if "grind" in site_lower:
        return f"{site_name} Drop", "drop_site", site_name, site_address
    if "connexus" in site_lower:
        return "Connexus Energy Ramsey Drop", "drop_site", site_name, site_address

    # Default new/unknown pickup-site options to drop sites so they are visible in routing prep.
    return f"{site_name} Drop", "drop_site", site_name, site_address


def _product_string(products):
    return "".join(str({
        "id": item.get("product_id", ""),
        "product": item.get("product_name", ""),
        "quantity": item.get("quantity", ""),
        "Product Options": item.get("product_options", ""),
    }) for item in products)


def _use_delivery_override(override: str) -> bool:
    text = _clean(override).lower()
    if not text or text in {"same", "n/a", "na", "none", "no", "non"}:
        return False
    return bool(re.search(r"\d", text) and len(text) >= 8)


def _build_notes(share_size: str, order_notes: str) -> str:
    share = _clean(share_size)
    notes = _clean(order_notes)

    if share and notes:
        return f"{share}: {notes}"
    if share:
        return f"{share}:"
    return notes


def build_clean_orders_dataframe(orders_df: pd.DataFrame) -> pd.DataFrame:
    df = orders_df.copy().fillna("")
    records = []

    for order_number, group in df.groupby("Order #", sort=False):
        group = group.fillna("")
        product_rows = group[group["Product Id"].astype(str).str.strip() != ""]
        products = []

        for _, product_row in product_rows.iterrows():
            products.append({
                "product_id": _clean(product_row.get("Product Id", "")),
                "product_name": _clean(product_row.get("Product Name", "")),
                "product_options": _clean(product_row.get("Product Options", "")),
                "quantity": _clean(product_row.get("Product Quantity", "")),
            })

        primary_product = products[0] if products else {"product_id": "", "product_name": "", "product_options": "", "quantity": ""}
        options = primary_product.get("product_options", "")
        pickup_site = _extract_option(options, "Pickup/Drop Site")
        delivery_override = _extract_option(options, "Delivery Address (If different from billing)")
        allergies = _extract_option(options, "Allergies (We will do our best to accommodate allergies, but cannot guarantee produce is free of cross contamination)")
        preferences = _extract_option(options, "Preferences (We will do our best to accommodate preferences, but cannot guarantee replacement items)")
        fulfillment, category, site_name, site_address = _fulfillment(primary_product.get("product_name", ""), pickup_site)

        address_1 = _first_non_empty(group["Shipping Address"])
        address_2 = _first_non_empty(group["Shipping Address 2"])
        city = _first_non_empty(group["Shipping City"])
        state = _first_non_empty(group["Shipping Region"])
        postal_code = _first_non_empty(group["Shipping Postal Code"])
        customer_address = _format_address(address_1, address_2, city, state, postal_code)

        if category == "drop_site":
            optimo_address = site_address
        elif category == "delivery" and _use_delivery_override(delivery_override):
            optimo_address = delivery_override.replace("\n", ", ")
        else:
            optimo_address = customer_address

        first_name = _first_non_empty(group["Shipping First Name"])
        last_name = _first_non_empty(group["Shipping Last Name"])
        share_size = _share_size(primary_product.get("product_name", ""))
        order_notes = _first_non_empty(group["Order Notes"])

        record = {
            "order_number": _clean(order_number),
            "date": _first_non_empty(group["Date"]),
            "status": _first_non_empty(group["Status"]),
            "first_name": first_name,
            "last_name": last_name,
            "email": _first_non_empty(group["Shipping Email"]),
            "address_1": address_1,
            "address_2": address_2,
            "postal_code": postal_code,
            "city": city,
            "state": state,
            "country": _first_non_empty(group["Shipping Country"]),
            "phone": _first_non_empty(group["Shipping Phone"]),
            "location_name": " ".join(part for part in [first_name, last_name] if part),
            "address": customer_address,
            "products": _product_string(products),
            "product_id": primary_product.get("product_id", ""),
            "product_name": primary_product.get("product_name", ""),
            "quantity": primary_product.get("quantity", ""),
            "product_options": options,
            "share_size": share_size,
            "pickup_drop_site": pickup_site,
            "delivery_address_override": delivery_override,
            "allergies": allergies,
            "preferences": preferences,
            "fulfillment": fulfillment,
            "fulfillment_category": category,
            "site_name": site_name,
            "site_address": site_address,
            "optimo_address": optimo_address,
            "order_notes": order_notes,
            "notes": _build_notes(share_size, order_notes),
        }
        records.append(record)

    return pd.DataFrame(records)


def build_working_orders_dataframe(clean_orders_df: pd.DataFrame) -> pd.DataFrame:
    columns = [
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
    return clean_orders_df.loc[:, columns].copy()


def build_optimo_dataframe(clean_orders_df: pd.DataFrame) -> pd.DataFrame:
    routable = clean_orders_df[clean_orders_df["fulfillment_category"].isin(["delivery", "drop_site"])].copy()
    return pd.DataFrame({
        "Location": routable["location_name"],
        "Address": routable["optimo_address"],
        "email": routable["email"],
        "phone": routable["phone"],
        "fulfillment": routable["fulfillment"],
        "notes": routable["notes"],
    })


def build_review_needed_dataframe(clean_orders_df: pd.DataFrame) -> pd.DataFrame:
    issues = []
    for _, row in clean_orders_df.iterrows():
        row_issues = []
        if not row.get("email"):
            row_issues.append("Missing email")
        if not row.get("phone"):
            row_issues.append("Missing phone")
        if row.get("fulfillment_category") == "unknown":
            row_issues.append("Unknown fulfillment - update parsing/config")
        if row.get("fulfillment_category") == "delivery" and not row.get("optimo_address"):
            row_issues.append("Delivery order missing address")
        override = row.get("delivery_address_override", "")
        if override and not _use_delivery_override(override) and _clean(override).lower() not in {"same", "none", "n/a", "na", "no", "non"}:
            row_issues.append(f"Check delivery address override: {override}")
        if row.get("fulfillment_category") == "drop_site" and not row.get("site_address"):
            row_issues.append("Drop site missing route address")
        if not row.get("share_size"):
            row_issues.append("Could not parse share size")

        if row_issues:
            issues.append({
                "order_number": row.get("order_number", ""),
                "customer": row.get("location_name", ""),
                "fulfillment": row.get("fulfillment", ""),
                "issues": "; ".join(row_issues),
                "product_options": row.get("product_options", ""),
                "notes": row.get("notes", ""),
            })

    return pd.DataFrame(issues)


def build_summary_dataframe(clean_orders_df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        clean_orders_df
        .groupby(["fulfillment_category", "fulfillment", "share_size"], dropna=False)
        .size()
        .reset_index(name="order_count")
        .sort_values(["fulfillment_category", "fulfillment", "share_size"])
    )
    return summary


def _autosize_excel_columns(writer, sheets) -> None:
    for sheet_name, dataframe in sheets.items():
        worksheet = writer.sheets[sheet_name]
        for column_index, column_name in enumerate(dataframe.columns):
            values = dataframe[column_name].astype(str).head(200).tolist()
            max_length = max([len(str(column_name)), *(len(value) for value in values)] or [10])
            worksheet.set_column(column_index, column_index, min(max(max_length + 2, 10), 45))
        worksheet.freeze_panes(1, 0)
        worksheet.autofilter(0, 0, max(len(dataframe), 1), max(len(dataframe.columns) - 1, 0))


def create_orders_workbook(orders_df: pd.DataFrame, output_path: Optional[str] = None) -> str:
    if output_path is None:
        output_path = asksaveasfile_xlsx_wrapper()

    clean_orders = build_clean_orders_dataframe(orders_df)
    optimo = build_optimo_dataframe(clean_orders)
    review_needed = build_review_needed_dataframe(clean_orders)
    summary = build_summary_dataframe(clean_orders)

    pickups = build_working_orders_dataframe(clean_orders[clean_orders["fulfillment_category"] == "pickup"].copy())
    deliveries = build_working_orders_dataframe(clean_orders[clean_orders["fulfillment_category"] == "delivery"].copy())
    drops = build_working_orders_dataframe(clean_orders[clean_orders["fulfillment_category"] == "drop_site"].copy())

    sheets = {
        "Raw Import": orders_df,
        "All Orders - Clean": clean_orders,
        "All Pickups": pickups,
        "All Deliveries": deliveries,
        "All Drops": drops,
        "Optimo Import": optimo,
        "Review Needed": review_needed,
        "Summary": summary,
    }

    with pd.ExcelWriter(output_path, engine="xlsxwriter") as writer:
        for sheet_name, dataframe in sheets.items():
            dataframe.to_excel(writer, sheet_name=sheet_name[:31], index=False)
        _autosize_excel_columns(writer, {name[:31]: df for name, df in sheets.items()})

    optimo_csv_path = str(Path(output_path).with_name(f"{Path(output_path).stem} - Optimo Import.csv"))
    optimo.to_csv(optimo_csv_path, index=False)
    return output_path


# Legacy CSV export retained in case you still need the older output shape.
def create_new_orders_csv(orders):
    file = asksaveasfile_csv_wrapper()
    with open(file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "order_number", "date", "status", "first_name", "last_name", "email", "address_1",
            "address_2", "postal_code", "city", "state", "country", "phone", "products", "notes",
            "delivery",
        ])
        for order in orders:
            writer.writerow([
                order.order_number, order.date, order.status, order.first_name, order.last_name,
                order.email, order.address_1, order.address_2, order.postal_code, order.city,
                order.state, order.country, order.phone, getattr(order, "products", ""),
                order.notes, order.delivery,
            ])
    return file


def print_orders_to_console(orders_list):
    print(f"PRINTING {len(orders_list)} ORDERS TO THE CONSOLE:")
    for order in orders_list:
        order.print_order()
