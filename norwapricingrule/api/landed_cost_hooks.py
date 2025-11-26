import frappe
from norwa_pricing_rules.utils.pricing import update_selling_price_for_item

def on_submit(doc, method=None):
    """
    Triggered when a Landed Cost Voucher is submitted.
    Since LCV adds costs (Freight, Customs) to the items, the Valuation Rate increases.
    We must trigger a price update to protect margins.
    """
    
    # 1. Identify all unique items affected by this Landed Cost Voucher
    affected_items = set()
    
    # The LCV has a table 'items' that lists the Purchase Receipts and Items involved
    for row in doc.get("items"):
        if row.item_code:
            affected_items.add(row.item_code)

    # 2. Loop through each item and update its price
    for item_code in affected_items:
        # We fetch the NEW Valuation Rate from the Item Master.
        # Why? Because when LCV is submitted, ERPNext automatically updates 
        # the 'valuation_rate' field on the Item record (Moving Average).
        new_valuation_rate = frappe.db.get_value("Item", item_code, "valuation_rate")

        if new_valuation_rate and new_valuation_rate > 0:
            # Re-run the pricing logic with the new higher cost
            update_selling_price_for_item(item_code, new_valuation_rate)
            
            # Optional: Log it for debugging
            frappe.logger().info(f"Landed Cost Updated: {item_code} new cost is {new_valuation_rate}")