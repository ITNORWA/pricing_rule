import frappe
from frappe.utils import flt, getdate


def apply_item_group_max_discount(doc, method=None):
	max_discount = get_applicable_max_discount(doc.name, doc.item_group)
	if max_discount is None:
		return

	doc.max_discount = flt(max_discount)


def get_applicable_max_discount(item_code, item_group):
	today = getdate(frappe.utils.nowdate())
	rules = frappe.get_all(
		"Item Group Discount Rule",
		filters={"is_enabled": 1, "start_date": ["<=", today]},
		fields=["name", "apply_on", "item_group", "max_discount_percentage", "end_date"],
	)
	if not rules:
		return None

	rule_names = [rule.name for rule in rules]
	items = frappe.get_all(
		"Discount Rule Item",
		filters={"parent": ["in", rule_names]},
		fields=["parent", "item_code"],
	)
	item_map = {}
	for row in items:
		item_map.setdefault(row.parent, []).append(row.item_code)

	item_specific = {}
	group_rules = {}
	for rule in rules:
		if rule.end_date and rule.end_date < today:
			continue
		if rule.apply_on == "Item":
			for code in item_map.get(rule.name, []):
				item_specific[code] = flt(rule.max_discount_percentage)
		elif rule.apply_on == "Item Group" and rule.item_group:
			group_rules[rule.item_group] = {
				"max_discount": flt(rule.max_discount_percentage),
				"items": set(item_map.get(rule.name, [])),
			}

	if item_code in item_specific:
		return item_specific[item_code]

	if item_group and item_group in group_rules:
		rule = group_rules[item_group]
		if rule["items"] and item_code not in rule["items"]:
			return None
		return rule["max_discount"]

	return None
