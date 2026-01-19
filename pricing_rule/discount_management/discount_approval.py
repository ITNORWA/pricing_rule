import frappe
from frappe.utils import flt, getdate, validate_email_address

APPROVAL_NOT_REQUESTED = "Draft"
APPROVAL_PENDING = "Pending Approval"
APPROVAL_APPROVED = "Approved"
APPROVAL_SUBMITTED = "Submitted"
EMAIL_NOTIFICATIONS_ENABLED = False


def validate_sales_doc(doc, method=None):
	if not doc.get("approval_status"):
		doc.approval_status = APPROVAL_NOT_REQUESTED

	doc.requires_discount_approval = 0

	if doc.doctype == "Sales Order" and doc.is_new():
		if doc.approval_status in (APPROVAL_APPROVED, APPROVAL_SUBMITTED) and _has_quotation_items(doc):
			doc.approval_status = APPROVAL_NOT_REQUESTED

	_exceeding = get_exceeding_items(doc)
	if doc.doctype == "Sales Order":
		needing = filter_exceeding_needing_approval(doc, _exceeding)
		doc.requires_discount_approval = 1 if needing else 0
	else:
		doc.requires_discount_approval = 1 if _exceeding else 0

	if not _exceeding:
		doc.requires_discount_approval = 0



def before_submit_sales_doc(doc, method=None):
	exceeding = get_exceeding_items(doc)
	if not exceeding:
		return

	needing = filter_exceeding_needing_approval(doc, exceeding)
	if doc.doctype == "Sales Order" and not needing:
		return

	if doc.approval_status != APPROVAL_APPROVED:
		if doc.approval_status != APPROVAL_SUBMITTED:
			frappe.throw(_build_exceeded_message(exceeding))


@frappe.whitelist()
def request_discount_approval(doctype, name):
	doc = frappe.get_doc(doctype, name)
	_validate_sales_doc_type(doc)
	_ensure_draft(doc)

	exceeding = get_exceeding_items(doc)
	if not exceeding:
		frappe.throw("No discounts exceed the limit for this document.")

	doc.approval_status = APPROVAL_PENDING
	doc.approval_comments = ""
	doc.save(ignore_permissions=True)

	if EMAIL_NOTIFICATIONS_ENABLED:
		_notify_sales_managers(doc)
	return {"status": doc.approval_status, "message": "Approval request submitted."}


@frappe.whitelist()
def approve_discount(doctype, name, comments=None):
	_ensure_sales_manager()
	doc = frappe.get_doc(doctype, name)
	_validate_sales_doc_type(doc)
	_ensure_draft(doc)

	doc.approval_status = APPROVAL_APPROVED
	if comments:
		doc.approval_comments = comments
	doc.save(ignore_permissions=True)

	if EMAIL_NOTIFICATIONS_ENABLED:
		_notify_requester(doc, "Approved")
	return {"status": doc.approval_status, "message": "Discount approved."}


@frappe.whitelist()
def reject_discount(doctype, name, comments=None):
	_ensure_sales_manager()
	doc = frappe.get_doc(doctype, name)
	_validate_sales_doc_type(doc)
	_ensure_draft(doc)

	doc.approval_status = APPROVAL_NOT_REQUESTED
	if comments:
		doc.approval_comments = comments
	doc.save(ignore_permissions=True)

	if EMAIL_NOTIFICATIONS_ENABLED:
		_notify_requester(doc, "Returned for amendment")
	return {"status": doc.approval_status, "message": "Returned for amendment."}


@frappe.whitelist()
def get_discount_status(doctype, name):
	doc = frappe.get_doc(doctype, name)
	_validate_sales_doc_type(doc)

	exceeding = get_exceeding_items(doc)
	needing = filter_exceeding_needing_approval(doc, exceeding)
	return {
		"requires_approval": bool(needing),
		"approval_status": doc.get("approval_status") or APPROVAL_NOT_REQUESTED,
		"exceeding_count": len(needing),
	}


def get_exceeding_items(doc):
	item_codes = [d.item_code for d in doc.items if d.item_code]
	if not item_codes:
		return []

	item_group_map = {
		row.name: row.item_group
		for row in frappe.get_all(
			"Item",
			filters={"name": ["in", item_codes]},
			fields=["name", "item_group"],
		)
	}

	allowed_rules = _get_active_rules()
	if not allowed_rules:
		return []

	item_rules = {}
	group_rules = {}
	for rule in allowed_rules:
		if rule.apply_on == "Item":
			for item_code in rule.get("items", []):
				item_rules[item_code] = rule.max_discount
		elif rule.apply_on == "Item Group" and rule.item_group:
			rule_items = rule.get("items", [])
			group_rules[rule.item_group] = {
				"max_discount": rule.max_discount,
				"items": set(rule_items) if rule_items else set(),
			}

	exceeding = []
	for item in doc.items:
		item_group = item_group_map.get(item.item_code)
		max_discount = None
		if item.item_code in item_rules:
			max_discount = item_rules[item.item_code]
		elif item_group and item_group in group_rules:
			rule = group_rules[item_group]
			if rule["items"] and item.item_code not in rule["items"]:
				continue
			max_discount = rule["max_discount"]
		if max_discount is None:
			continue

		discount_percent = get_discount_percentage(item)
		if discount_percent > max_discount:
			exceeding.append(
				{
					"item_code": item.item_code,
					"item_group": item_group,
					"discount_percent": discount_percent,
					"max_discount": max_discount,
					"exceeded_by": discount_percent - max_discount,
					"quotation_item": getattr(item, "quotation_item", None),
				}
			)

	return exceeding


def _get_active_rules():
	today = getdate(frappe.utils.nowdate())
	rules = frappe.get_all(
		"Item Group Discount Rule",
		filters={"is_enabled": 1, "start_date": ["<=", today]},
		fields=["name", "apply_on", "item_group", "max_discount_percentage", "end_date"],
	)
	if not rules:
		return []

	rule_names = [rule.name for rule in rules]
	items = frappe.get_all(
		"Discount Rule Item",
		filters={"parent": ["in", rule_names]},
		fields=["parent", "item_code"],
	)
	item_map = {}
	for row in items:
		item_map.setdefault(row.parent, []).append(row.item_code)

	active_rules = []
	for rule in rules:
		rule_end = getdate(rule.end_date) if rule.end_date else None
		if rule_end and rule_end < today:
			continue
		active_rules.append(
			frappe._dict(
				{
					"name": rule.name,
					"apply_on": rule.apply_on,
					"item_group": rule.item_group,
					"max_discount": flt(rule.max_discount_percentage),
					"items": item_map.get(rule.name, []),
				}
			)
		)
	return active_rules


def filter_exceeding_needing_approval(doc, exceeding):
	if doc.doctype != "Sales Order":
		return exceeding

	approved_quotation_map = _get_approved_quotation_map(doc)
	if not approved_quotation_map:
		return exceeding

	return [
		row for row in exceeding if not _is_covered_by_approved_quotation(row, approved_quotation_map)
	]


def _get_approved_quotation_map(doc):
	quotation_items = [d.quotation_item for d in doc.items if getattr(d, "quotation_item", None)]
	if not quotation_items:
		return {}

	quotation_item_rows = frappe.get_all(
		"Quotation Item",
		filters={"name": ["in", quotation_items]},
		fields=["name", "parent"],
	)
	quotation_map = {row.name: row.parent for row in quotation_item_rows}
	if not quotation_map:
		return {}

	approved = frappe.get_all(
		"Quotation",
		filters={
			"name": ["in", list(quotation_map.values())],
			"approval_status": ["in", [APPROVAL_APPROVED, APPROVAL_SUBMITTED]],
		},
		pluck="name",
	)
	return {"quotation_map": quotation_map, "approved": set(approved)}


def _is_covered_by_approved_quotation(row, approved_quotation_map):
	quotation_map = approved_quotation_map.get("quotation_map") or {}
	approved = approved_quotation_map.get("approved") or set()
	quotation_item = row.get("quotation_item")
	if not quotation_item:
		return False

	quotation_name = quotation_map.get(quotation_item)
	return quotation_name in approved


def get_discount_percentage(item):
	discount_percentage = flt(getattr(item, "discount_percentage", 0))
	if discount_percentage:
		return discount_percentage

	discount_amount = flt(getattr(item, "discount_amount", 0))
	price_list_rate = flt(getattr(item, "price_list_rate", 0))
	if discount_amount and price_list_rate:
		return (discount_amount / price_list_rate) * 100

	return 0.0


def _build_exceeded_message(exceeding_items):
	lines = []
	for row in exceeding_items:
		lines.append(
			(
				f"Item {row['item_code']}: discount {row['discount_percent']:.2f}% "
				f"exceeds limit {row['max_discount']:.2f}% by {row['exceeded_by']:.2f}%."
			)
		)
	return "Discount exceeds limit. Request approval from Sales Manager.<br>" + "<br>".join(lines)


def _has_quotation_items(doc):
	return any(getattr(item, "quotation_item", None) for item in doc.items)


def notify_exceeded_on_save(doc, method=None):
	if doc.docstatus != 0:
		return

	if getattr(doc, "_action", None) not in ("save", None):
		return

	if doc.flags.get("_discount_notice_shown") or getattr(frappe.flags, "_discount_notice_shown", False):
		return

	if doc.approval_status in (APPROVAL_APPROVED, APPROVAL_SUBMITTED):
		return

	exceeding = get_exceeding_items(doc)
	if not exceeding:
		return

	doc.flags._discount_notice_shown = True
	frappe.flags._discount_notice_shown = True
	frappe.msgprint(
		_build_exceeded_message(exceeding),
		title="Discount exceeds limit",
		indicator="red",
	)


def before_validate_sales_order(doc, method=None):
	# Ensure new Sales Orders from Quotation start in Draft workflow state.
	if doc.is_new() and _has_quotation_items(doc):
		if doc.approval_status in (APPROVAL_APPROVED, APPROVAL_SUBMITTED):
			doc.approval_status = APPROVAL_NOT_REQUESTED


def _validate_sales_doc_type(doc):
	if doc.doctype not in ("Quotation", "Sales Order"):
		frappe.throw("Unsupported document for discount approval.")


def _ensure_sales_manager():
	roles = frappe.get_roles(frappe.session.user)
	if "Sales Manager" not in roles:
		frappe.throw("Only Sales Managers can approve or reject discounts.")


def _ensure_draft(doc):
	if doc.docstatus != 0:
		frappe.throw("Discount approvals can only be requested on draft documents.")


def _notify_sales_managers(doc):
	managers = frappe.get_all("Has Role", filters={"role": "Sales Manager"}, pluck="parent")
	if not managers:
		return

	user_emails = frappe.get_all(
		"User",
		filters={"name": ["in", managers], "enabled": 1},
		fields=["name", "email"],
	)
	recipients = []
	for user in user_emails:
		email = _get_user_email(user)
		if email:
			recipients.append(email)
	if not recipients:
		return

	subject = f"{doc.doctype} {doc.name} pending discount approval"
	message = f"{doc.doctype} {doc.name} requires approval for discounts above limits."
	frappe.sendmail(recipients=recipients, subject=subject, message=message)


def _notify_requester(doc, action):
	if not doc.owner:
		return

	user = frappe.db.get_value("User", doc.owner, ["name", "email"], as_dict=True)
	if not user:
		return
	email = _get_user_email(user)
	if not email:
		return

	subject = f"{doc.doctype} {doc.name} discount {action.lower()}"
	message = f"Discount request for {doc.doctype} {doc.name} was {action.lower()}."
	frappe.sendmail(recipients=[email], subject=subject, message=message)


def _get_user_email(user_row):
	email = user_row.get("email") or user_row.get("name")
	return validate_email_address(email) if email else None
