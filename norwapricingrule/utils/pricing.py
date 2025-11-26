import frappe
from frappe.utils import today, getdate
from frappe.utils.nestedset import get_ancestors_of

def get_pricing_config_for_item(item_code: str) -> dict:
    """
    Return merged pricing config.
    Priority: 
    1. Item Override
    2. Item Group Profile (Specific, Active, Within Date)
    3. Parent Group Profile (Active, Within Date)
    """
    item = frappe.get_doc("Item", item_code)

    # 1. Check for specific Item Overrides (Highest Priority)
    if item.get("norwa_margin_type") or item.get("norwa_max_discount_percent"):
        return {
            "margin_type": item.get("norwa_margin_type") or "Markup %",
            "margin_value": item.get("norwa_margin_value") or 0,
            "max_discount_percent": item.get("norwa_max_discount_percent") or 0,
            "price_list": item.get("norwa_price_list") or "Standard Selling",
            "is_active": 1,
        }

    # 2. Hierarchy Logic: Check Item Group and its Ancestors
    item_group = item.item_group
    ancestors = get_ancestors_of("Item Group", item_group)
    
    # Search Order: [Current Group, Parent, Grandparent, Root]
    search_groups = [item_group] + list(reversed(ancestors))
    
    current_date = getdate(today())

    for group_name in search_groups:
        # Fetch ALL profiles for this group that are marked active
        profiles = frappe.get_all(
            "Item Group Pricing Profile",
            filters={"item_group": group_name, "is_active": 1},
            fields=["name", "margin_type", "margin_value", "max_discount_percent", 
                    "price_list", "valid_from", "valid_upto"]
        )

        # Loop through found profiles and check Dates
        for profile in profiles:
            valid_from = getdate(profile.valid_from) if profile.valid_from else None
            valid_upto = getdate(profile.valid_upto) if profile.valid_upto else None

            # Logic: 
            # 1. If no dates are set -> Always Valid
            # 2. If dates are set -> Must be within range
            is_valid_date = True
            
            if valid_from and current_date < valid_from:
                is_valid_date = False
            if valid_upto and current_date > valid_upto:
                is_valid_date = False

            if is_valid_date:
                # Found a valid profile! Return it.
                return profile

    # If nothing found after checking the whole tree
    return None

def update_selling_price_for_item(item_code: str, buying_rate: float):
    """Updates the selling price for the given item based on its pricing config."""
    config = get_pricing_config_for_item(item_code)
    
    if not config:
        return

    selling_price = calculate_selling_price(buying_rate, config)
    price_list = config.get("price_list") or "Standard Selling"

    # Get the correct currency from the Price List
    price_list_currency = frappe.db.get_value("Price List", price_list, "currency")
    if not price_list_currency:
        price_list_currency = frappe.db.get_single_value("Global Defaults", "default_currency")

    # Check/Update Item Price
    item_price_name = frappe.db.get_value(
        "Item Price",
        {"item_code": item_code, "price_list": price_list, "selling": 1},
        "name"
    )

    if item_price_name:
        ip = frappe.get_doc("Item Price", item_price_name)
        ip.price_list_rate = selling_price
        ip.currency = price_list_currency
        ip.flags.ignore_permissions = True
        ip.save()
    else:
        ip = frappe.new_doc("Item Price")
        ip.update({
            "item_code": item_code,
            "price_list": price_list,
            "price_list_rate": selling_price,
            "selling": 1,
            "currency": price_list_currency,
        })
        ip.flags.ignore_permissions = True
        ip.insert()

def calculate_selling_price(buying_rate: float, config: dict) -> float:
    margin_type = config.get("margin_type") or "Markup %"
    margin_value = float(config.get("margin_value") or 0)

    if margin_type == "Markup %":
        return round(buying_rate * (1 + margin_value / 100.0), 2)
    elif margin_type == "Fixed Margin":
        return round(buying_rate + margin_value, 2)
    else:
        return round(buying_rate, 2)