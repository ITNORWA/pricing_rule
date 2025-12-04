app_name = "discount_control"
app_title = "Discount Control"
app_publisher = "Your Name"
app_description = "Manage Item Group Discounts"
app_email = "manyisanewton26@email.com"
app_license = "MIT"

# DocType Events
# This is where we intercept the Sales Order
doc_events = {
    "Sales Order": {
        "validate": "discount_control.overrides.sales_order_check.validate_discounts",
        "on_submit": "discount_control.overrides.sales_order_check.check_approval_on_submit"
    }
}

# Fixtures
# This tells ERPNext to look into the fixtures folder and apply the changes
fixtures = [
    {"dt": "Custom Field", "filters": [["module", "=", "Discount Control"]]},
    {"dt": "Workflow State", "filters": [["name", "in", ["Pending Approval", "To Amend"]]]},
    {"dt": "Workflow", "filters": [["name", "=", "Discount Control Workflow"]]}
]