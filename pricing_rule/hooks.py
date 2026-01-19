app_name = "pricing_rule"
app_title = "Pricing Rule"
app_publisher = "Newton Manyisa"
app_description = "Custom discount management app for ERPNext"
app_email = "admin@example.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "pricing_rule",
# 		"logo": "/assets/pricing_rule/logo.png",
# 		"title": "Pricing Rule",
# 		"route": "/pricing_rule",
# 		"has_permission": "pricing_rule.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/pricing_rule/css/pricing_rule.css"
# app_include_js = "/assets/pricing_rule/js/pricing_rule.js"

# include js, css files in header of web template
# web_include_css = "/assets/pricing_rule/css/pricing_rule.css"
# web_include_js = "/assets/pricing_rule/js/pricing_rule.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "pricing_rule/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
doctype_js = {
	"Quotation": "public/js/quotation.js",
	"Sales Order": "public/js/sales_order.js",
	"Item": "public/js/item.js",
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "pricing_rule/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "pricing_rule.utils.jinja_methods",
# 	"filters": "pricing_rule.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "pricing_rule.install.before_install"
# after_install = "pricing_rule.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "pricing_rule.uninstall.before_uninstall"
# after_uninstall = "pricing_rule.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "pricing_rule.utils.before_app_install"
# after_app_install = "pricing_rule.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "pricing_rule.utils.before_app_uninstall"
# after_app_uninstall = "pricing_rule.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "pricing_rule.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }
override_doctype_class = {
	"Quotation": "pricing_rule.overrides.quotation.Quotation",
	"Sales Order": "pricing_rule.overrides.sales_order.SalesOrder",
	"Sales Invoice": "pricing_rule.overrides.sales_invoice.SalesInvoice",
}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Quotation": {
		"validate": "pricing_rule.discount_management.discount_approval.validate_sales_doc",
		"before_save": "pricing_rule.discount_management.discount_approval.notify_exceeded_on_save",
		"before_submit": "pricing_rule.discount_management.discount_approval.before_submit_sales_doc",
	},
	"Sales Order": {
		"before_validate": "pricing_rule.discount_management.discount_approval.before_validate_sales_order",
		"before_insert": "pricing_rule.discount_management.discount_approval.before_validate_sales_order",
		"before_save": [
			"pricing_rule.discount_management.discount_approval.before_validate_sales_order",
			"pricing_rule.discount_management.discount_approval.notify_exceeded_on_save",
		],
		"validate": "pricing_rule.discount_management.discount_approval.validate_sales_doc",
		"before_submit": "pricing_rule.discount_management.discount_approval.before_submit_sales_doc",
	},
	"Item": {
		"validate": "pricing_rule.discount_management.discount_rules.apply_item_group_max_discount",
	},
	"Purchase Receipt": {
		"on_submit": "pricing_rule.discount_management.landed_cost.handle_purchase_receipt",
	},
	"Landed Cost Voucher": {
		"on_submit": "pricing_rule.discount_management.landed_cost.handle_landed_cost_voucher",
	},
}

fixtures = [
	"Custom Field",
	"Module Def",
	"Workflow",
	"Workflow State",
	"Workflow Action Master",
]

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"pricing_rule.tasks.all"
# 	],
# 	"daily": [
# 		"pricing_rule.tasks.daily"
# 	],
# 	"hourly": [
# 		"pricing_rule.tasks.hourly"
# 	],
# 	"weekly": [
# 		"pricing_rule.tasks.weekly"
# 	],
# 	"monthly": [
# 		"pricing_rule.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "pricing_rule.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "pricing_rule.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "pricing_rule.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["pricing_rule.utils.before_request"]
# after_request = ["pricing_rule.utils.after_request"]

# Job Events
# ----------
# before_job = ["pricing_rule.utils.before_job"]
# after_job = ["pricing_rule.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"pricing_rule.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }
