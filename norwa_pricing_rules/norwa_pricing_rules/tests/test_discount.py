import frappe
from norwa_pricing_rules.api.discount_hooks import validate_discount

# --- Helper Functions ---
def setup_discount_test_data():
    """Ensure we have the necessary groups and profiles."""
    if not frappe.db.exists("Item Group", "Discount Test Group"):
        frappe.get_doc({
            "doctype": "Item Group",
            "item_group_name": "Discount Test Group",
            "parent_item_group": "All Item Groups"
        }).insert()

    # Create Profile: Max Discount 10%
    if not frappe.db.exists("Item Group Pricing Profile", "Profile-Discount-Test"):
        frappe.get_doc({
            "doctype": "Item Group Pricing Profile",
            "name": "Profile-Discount-Test",
            "item_group": "Discount Test Group",
            "max_discount_percent": 10,  # Matches your utils logic
            "is_active": 1
        }).insert()

    # Create Item
    if not frappe.db.exists("Item", "DISCOUNT-ITEM-01"):
        frappe.get_doc({
            "doctype": "Item",
            "item_code": "DISCOUNT-ITEM-01",
            "item_name": "Test Discount Item",
            "item_group": "Discount Test Group",
            "stock_uom": "Nos"
        }).insert()

# --- The Tests ---

def test_discount_violation():
    setup_discount_test_data()
    
    # 1. Create Order with 15% discount (Allowed is 10%)
    so = frappe.new_doc("Sales Order")
    so.customer = "_Test Customer"
    so.append("items", {
        "item_code": "DISCOUNT-ITEM-01",
        "qty": 1,
        "rate": 100,
        "discount_percentage": 15 
    })
    
    # Run Validation
    validate_discount(so)
    
    # Assert: Flag should be 1
    assert so.norwa_requires_discount_approval == 1, "Should require approval for 15% discount"

def test_discount_safe():
    setup_discount_test_data()
    
    # 2. Create Order with 5% discount (Allowed is 10%)
    so = frappe.new_doc("Sales Order")
    so.customer = "_Test Customer"
    so.append("items", {
        "item_code": "DISCOUNT-ITEM-01",
        "qty": 1,
        "rate": 100,
        "discount_percentage": 5 
    })
    
    validate_discount(so)
    
    # Assert: Flag should be 0
    assert so.norwa_requires_discount_approval == 0, "Should NOT require approval for 5% discount"

def test_global_discount_loophole():
    setup_discount_test_data()

    # 3. Create Order with 0% item discount, but 20% Global Discount
    so = frappe.new_doc("Sales Order")
    so.customer = "_Test Customer"
    so.additional_discount_percentage = 20 # The Loophole
    so.append("items", {
        "item_code": "DISCOUNT-ITEM-01",
        "qty": 1,
        "rate": 100,
        "discount_percentage": 0
    })

    validate_discount(so)

    # Assert: Flag should be 1 because global discount > 5% (limit set in code)
    assert so.norwa_requires_discount_approval == 1, "Global discount loophole should be caught"