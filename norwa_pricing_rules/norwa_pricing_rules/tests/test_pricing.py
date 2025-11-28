import frappe
from norwa_pricing_rules.utils.pricing import update_selling_price_for_item

# --- Helper Functions ---
def setup_pricing_data():
    """Create distinct groups for Markup tests and Hierarchy tests."""
    
    # Ensure Price List exists
    if not frappe.db.exists("Price List", "Standard Selling"):
        frappe.get_doc({"doctype": "Price List", "price_list_name": "Standard Selling", "selling": 1}).insert()

    # GROUP A: Direct Markup Test
    if not frappe.db.exists("Item Group", "Markup Test Group"):
        frappe.get_doc({"doctype": "Item Group", "item_group_name": "Markup Test Group", "parent_item_group": "All Item Groups"}).insert()

    # Profile: Cost + 50%
    if not frappe.db.exists("Item Group Pricing Profile", "Profile-Markup-50"):
        frappe.get_doc({
            "doctype": "Item Group Pricing Profile",
            "item_group": "Markup Test Group",
            "margin_type": "Markup %",
            "margin_value": 50,
            "price_list": "Standard Selling",
            "is_active": 1
        }).insert()

    # Item in Group A
    if not frappe.db.exists("Item", "PRICING-ITEM-01"):
        frappe.get_doc({"doctype": "Item", "item_code": "PRICING-ITEM-01", "item_group": "Markup Test Group", "stock_uom": "Nos"}).insert()

def setup_hierarchy_data():
    # GROUP B: Parent Group (Has Profile)
    if not frappe.db.exists("Item Group", "Parent Group"):
        frappe.get_doc({"doctype": "Item Group", "item_group_name": "Parent Group", "parent_item_group": "All Item Groups"}).insert()
        
    # Profile on PARENT: Cost + 20%
    if not frappe.db.exists("Item Group Pricing Profile", "Profile-Parent-20"):
        frappe.get_doc({
            "doctype": "Item Group Pricing Profile",
            "item_group": "Parent Group",
            "margin_type": "Markup %",
            "margin_value": 20,
            "price_list": "Standard Selling",
            "is_active": 1
        }).insert()

    # GROUP C: Child Group (No Profile, but child of Parent)
    if not frappe.db.exists("Item Group", "Child Group"):
        frappe.get_doc({"doctype": "Item Group", "item_group_name": "Child Group", "parent_item_group": "Parent Group"}).insert()

    # Item in Group C (Child)
    if not frappe.db.exists("Item", "HIERARCHY-ITEM"):
        frappe.get_doc({"doctype": "Item", "item_code": "HIERARCHY-ITEM", "item_group": "Child Group", "stock_uom": "Nos"}).insert()

# --- The Tests ---

def test_markup_calculation():
    setup_pricing_data()

    # Cost is 100. Margin is 50%. Selling Price should be 150.
    update_selling_price_for_item("PRICING-ITEM-01", buying_rate=100.0)

    # Fetch result from DB
    price = frappe.db.get_value("Item Price", 
        {"item_code": "PRICING-ITEM-01", "price_list": "Standard Selling"}, 
        "price_list_rate"
    )

    assert price == 150.0, f"Expected 150.0, got {price}"

def test_hierarchy_inheritance():
    """Test if item in Child Group inherits profile from Parent Group."""
    setup_hierarchy_data()

    # Cost is 100. Parent Margin is 20%. Selling Price should be 120.
    update_selling_price_for_item("HIERARCHY-ITEM", buying_rate=100.0)

    price = frappe.db.get_value("Item Price", 
        {"item_code": "HIERARCHY-ITEM", "price_list": "Standard Selling"}, 
        "price_list_rate"
    )

    assert price == 120.0, f"Expected 120.0 (inherited from parent), got {price}"