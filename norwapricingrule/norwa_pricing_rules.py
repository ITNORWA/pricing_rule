import frappe
from frappe import _

def install():
    """Run on app install: Set up necessary configurations, custom fields, etc."""
    # Create default Item Group Pricing Profiles if necessary
    create_default_pricing_profiles()

def create_default_pricing_profiles():
    """Create default pricing profiles for Item Groups."""
    item_group = "Chemicals"  # This is an example, you can add more groups

    # Check if the profile already exists, create if not
    existing_profile = frappe.db.exists("Item Group Pricing Profile", {"item_group": item_group})
    if not existing_profile:
        profile = frappe.get_doc({
            "doctype": "Item Group Pricing Profile",
            "item_group": item_group,
            "margin_type": "Markup %",
            "margin_value": 20,  
            "max_discount_percent": 10,  
            "price_list": "Standard Selling",  
            "is_active": 1,
        }).insert()
        frappe.db.commit()

    frappe.msgprint(_("Default pricing profile for 'Chemicals' created."))

def after_install():
    """Post-installation hook."""
    # You could add more post-installation tasks here
    pass

def before_uninstall():
    """Run cleanup tasks before app uninstallation."""
    pass

def uninstall():
    """Run on app uninstall: Clean up configurations, custom fields, etc."""
    # Clean up custom fields, workflows, etc.
    delete_default_pricing_profiles()

def delete_default_pricing_profiles():
    """Delete default pricing profiles if they exist."""
    if frappe.db.exists("Item Group Pricing Profile", {"item_group": "Chemicals"}):
        frappe.delete_doc("Item Group Pricing Profile", "Chemicals")
        frappe.db.commit()
    
    frappe.msgprint(_("Default pricing profile for 'Chemicals' deleted."))

def validate_pricing_rules():
    """Validate the pricing rule configuration."""
    # This function can be called manually to check if the pricing rules are correct
    pricing_profiles = frappe.get_all("Item Group Pricing Profile", fields=["item_group", "margin_type", "margin_value", "max_discount_percent"])
    if not pricing_profiles:
        frappe.throw(_("No pricing profiles found. Please configure at least one profile."))
    
    for profile in pricing_profiles:
        if profile.margin_value <= 0:
            frappe.throw(_("Margin value must be greater than 0 for Item Group: {}".format(profile.item_group)))
    
    frappe.msgprint(_("Pricing rules validated successfully."))
