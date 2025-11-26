import frappe
from norwa_pricing_rules.utils.pricing import update_selling_price_for_item

def on_submit(doc, method=None):
    """
    When Purchase Receipt is submitted, update selling prices
    for each item based on Item Group Pricing Profile or Item override.
    """
    
    # FIX 1: Handle Returns
    # If this is a Return (sending goods back), do NOT update selling prices.
    if doc.get("is_return"):
        return

    for item_row in doc.items:
        # Skip lines with no item code or no valuation rate (e.g. non-stock items)
        if not item_row.item_code or not item_row.valuation_rate:
            continue

        # Call the utility to calculate and update price
        update_selling_price_for_item(
            item_code=item_row.item_code, 
            buying_rate=item_row.valuation_rate
        )