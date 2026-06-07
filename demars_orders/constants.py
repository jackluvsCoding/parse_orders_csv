"""Shared constants used throughout the CSA order processor.

Keeping column names and tab names in one place makes the project easier to
maintain when Weebly, OptimoRoute, or the farm workflow changes.
"""

# Raw Weebly export columns used by the parser.
# These names must match the CSV headers exported from Weebly.
ORDER_NUMBER_COLUMN = "Order #"
ORDER_DATE_COLUMN = "Date"
ORDER_STATUS_COLUMN = "Status"
ORDER_NOTES_COLUMN = "Order Notes"

SHIPPING_FIRST_NAME_COLUMN = "Shipping First Name"
SHIPPING_LAST_NAME_COLUMN = "Shipping Last Name"
SHIPPING_EMAIL_COLUMN = "Shipping Email"
SHIPPING_ADDRESS_1_COLUMN = "Shipping Address"
SHIPPING_ADDRESS_2_COLUMN = "Shipping Address 2"
SHIPPING_POSTAL_CODE_COLUMN = "Shipping Postal Code"
SHIPPING_CITY_COLUMN = "Shipping City"
SHIPPING_REGION_COLUMN = "Shipping Region"
SHIPPING_COUNTRY_COLUMN = "Shipping Country"
SHIPPING_PHONE_COLUMN = "Shipping Phone"

PRODUCT_ID_COLUMN = "Product Id"
PRODUCT_NAME_COLUMN = "Product Name"
PRODUCT_OPTIONS_COLUMN = "Product Options"
PRODUCT_QUANTITY_COLUMN = "Product Quantity"

# Product option labels used inside Weebly's free-form `Product Options` value.
# Example:
#   Pickup/Drop Site : Roseville Neighborhood Pickup (Sunday PM), Preferences : ...
PICKUP_DROP_SITE_OPTION = "Pickup/Drop Site"
DELIVERY_ADDRESS_OVERRIDE_OPTION = "Delivery Address (If different from billing)"
ALLERGIES_OPTION = (
    "Allergies (We will do our best to accommodate allergies, "
    "but cannot guarantee produce is free of cross contamination)"
)
PREFERENCES_OPTION = (
    "Preferences (We will do our best to accommodate preferences, "
    "but cannot guarantee replacement items)"
)

PRODUCT_OPTION_LABELS = [
    PICKUP_DROP_SITE_OPTION,
    DELIVERY_ADDRESS_OVERRIDE_OPTION,
    ALLERGIES_OPTION,
    PREFERENCES_OPTION,
]

# Values customers might type when the delivery address is the same as their
# billing/shipping address. These are intentionally ignored as route overrides.
IGNORED_DELIVERY_OVERRIDE_VALUES = {"same", "n/a", "na", "none", "no", "non"}

# Internal fulfillment categories used to decide which workbook tabs and
# OptimoRoute outputs a row belongs to.
FULFILLMENT_CATEGORY_DELIVERY = "delivery"
FULFILLMENT_CATEGORY_DROP_SITE = "drop_site"
FULFILLMENT_CATEGORY_PICKUP = "pickup"
FULFILLMENT_CATEGORY_UNKNOWN = "unknown"

# Workbook tab names.
RAW_IMPORT_SHEET = "Raw Import"
CLEAN_ORDERS_SHEET = "All Orders - Clean"
PICKUPS_SHEET = "All Pickups"
DELIVERIES_SHEET = "All Deliveries"
DROPS_SHEET = "All Drops"
OPTIMO_IMPORT_SHEET = "Optimo Import"
REVIEW_NEEDED_SHEET = "Review Needed"
SUMMARY_SHEET = "Summary"

DEFAULT_OUTPUT_WORKBOOK_NAME = "DeMars Farms Orders - Generated.xlsx"
OPTIMO_IMPORT_SUFFIX = " - Optimo Import.csv"
