from . import __version__ as app_version

app_name = "norwa_pricing_rules"
app_title = "Norwa Pricing Rules"
app_publisher = "Your Company"
app_description = "This app manages item price updates based on purchase receipts and enforces discount approval workflows"
app_icon = "octicon octicon-file-directory"
app_color = "blue"
app_email = "manyisanewton26@gmail.com"
app_license = "MIT"

doc_events = {
    "Purchase Receipt": {
        "on_submit": "norwa_pricing_rules.api.purchase_receipt_hooks.on_submit"
    },
    "Landed Cost Voucher": {
        "on_submit": "norwa_pricing_rules.api.landed_cost_hooks.on_submit"
    },
    "Sales Order": {
        "validate": "norwa_pricing_rules.api.discount_hooks.validate_discount"
    },
    "Sales Invoice": {
        "validate": "norwa_pricing_rules.api.discount_hooks.validate_discount"
    },
}

fixtures = [
    "Custom Field",
    "Workflow State",
    "Workflow Action Master",
    "Workflow"
]