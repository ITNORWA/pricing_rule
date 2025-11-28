import frappe
from norwa_pricing_rules.utils.pricing import get_pricing_config_for_item

def validate_discount(doc, method=None):
    """
    Runs on validate for Sales Order / Sales Invoice.
    1. Checks Line Item Discounts.
    2. Checks Global (Additional) Discount.
    3. Sets 'norwa_requires_discount_approval' flag.
    """
    max_violation = 0
    requires_approval = False

    # 1. Check Line Items
    for row in doc.items:
        allowed = get_allowed_discount_percent(row.item_code)
        actual = abs(row.discount_percentage or 0)

        if actual > allowed:
            requires_approval = True
            if actual > max_violation:
                max_violation = actual

    # 2. Check Global Loophole (Additional Discount on Grand Total)
    global_discount = doc.additional_discount_percentage or 0
    
    # We apply a strict rule: If global discount > 0, we check it against 
    # a general threshold (e.g., the lowest allowed limit in the cart or a fixed 5%).
    # For now, let's assume if Global Discount > 5%, it needs approval.
    GLOBAL_DISCOUNT_LIMIT = 5.0 
    
    if global_discount > GLOBAL_DISCOUNT_LIMIT:
        requires_approval = True
        if global_discount > max_violation:
            max_violation = global_discount

    # 3. Set the Flag (Do NOT throw error, let Workflow handle it)
    if requires_approval:
        doc.norwa_requires_discount_approval = 1
        
        # Optional: Add a comment so the user knows why
        if not doc.get("__islocal"): # Only show message if not a new unsaved doc
            frappe.msgprint(
                f"⚠️ Discount Approval Required: A discount of {max_violation}% exceeds the allowed limit.",
                alert=True
            )
    else:
        doc.norwa_requires_discount_approval = 0

def get_allowed_discount_percent(item_code: str) -> float:
    """Return max discount allowed for item: item override > group profile."""
    config = get_pricing_config_for_item(item_code)
    if not config:
        # If no profile exists, assume 0% allowed (Strict) 
        # OR return 100% if you want to allow everything by default.
        return 0.0

    return float(config.get("max_discount_percent") or 0)