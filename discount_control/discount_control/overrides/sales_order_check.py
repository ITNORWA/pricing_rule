import frappe

def validate_discounts(doc, method):
    """
    Runs on Save. 
    Checks if any item exceeds the allowed discount set in 'Item Group Discount Rule'.
    Sets 'custom_needs_manager_approval' to 1 (True) or 0 (False).
    """
    
    # 1. Reset the flag to 0 (Clean Slate)
    doc.custom_needs_manager_approval = 0
    violation_found = False

    # 2. Loop through items to check violations
    for item in doc.items:
        # Fetch the rule from the database
        max_discount = frappe.db.get_value(
            "Item Group Discount Rule",
            {"item_group": item.item_group},
            "max_discount_percentage"
        )

        # If no rule exists, skip this item
        if max_discount is None:
            continue

        allowed = float(max_discount)
        given = float(item.discount_percentage or 0)

        # 3. Check Math
        if given > allowed:
            violation_found = True
            
            # Show a helpful message to the Sales User
            frappe.msgprint(
                msg=f"<b>Discount Warning:</b> Item '{item.item_code}' has {given}% discount (Limit: {allowed}%).<br>This order requires <b>Sales Manager</b> approval.",
                title="Approval Required",
                indicator="orange",
                alert=True
            )
            break # One violation is enough

    # 4. Set the flag based on findings
    if violation_found:
        doc.custom_needs_manager_approval = 1
    else:
        doc.custom_needs_manager_approval = 0

def check_approval_on_submit(doc, method):
    """
    Runs on Submit.
    Acts as a final security barrier. Even if someone bypasses the UI,
    this blocks the database transaction if roles are wrong.
    """
    if doc.custom_needs_manager_approval == 1:
        # Get the current user's roles
        user_roles = frappe.get_roles(frappe.session.user)
        
        # Allowed roles for high discount
        allowed_roles = ["Sales Manager", "System Manager", "Administrator"]
        
        # Check if user has permission
        if not any(role in user_roles for role in allowed_roles):
            frappe.throw(
                msg="<b>Permission Denied:</b> You are not authorized to submit this order due to high discounts.<br>Please ask your <b>Sales Manager</b> to approve it.",
                title="Strict Policy"
            )