import frappe
from frappe.utils import flt
from erpnext.stock.doctype.purchase_receipt.purchase_receipt import (
	get_item_account_wise_additional_cost,
)


def handle_purchase_receipt(doc, method=None):
	_update_items_from_receipt(doc.name)


def handle_landed_cost_voucher(doc, method=None):
	for receipt in doc.purchase_receipts:
		if receipt.receipt_document:
			_update_items_from_receipt(receipt.receipt_document)


@frappe.whitelist()
def recalculate_for_item(item_code):
	item_doc = frappe.get_doc("Item", item_code)
	if not item_doc.get("is_imported"):
		return "Item is not marked as imported."

	latest = frappe.get_all(
		"Purchase Receipt Item",
		filters={"item_code": item_code, "docstatus": 1},
		fields=["parent", "name", "base_rate", "base_net_rate", "rate", "qty"],
		order_by="creation desc",
		limit=1,
	)
	if not latest:
		return "No submitted Purchase Receipt found for this item."

	row = latest[0]
	_update_item_from_receipt_item(item_code, row, row.parent)
	return "Selling price recalculated from latest Purchase Receipt."


def _update_items_from_receipt(receipt_name):
	receipt = frappe.get_doc("Purchase Receipt", receipt_name)
	additional_costs = get_item_account_wise_additional_cost(receipt_name) or {}

	for item in receipt.items:
		if not _is_imported_item(item.item_code):
			continue

		_update_item_from_receipt_item(item.item_code, item, receipt_name, additional_costs)


def _update_item_from_receipt_item(item_code, receipt_item, receipt_name, additional_costs=None):
	additional_costs = additional_costs or {}

	purchase_cost = flt(
		receipt_item.get("base_rate") or receipt_item.get("base_net_rate") or receipt_item.get("rate")
	)
	qty = flt(receipt_item.get("qty")) or 1

	account_costs = additional_costs.get((item_code, receipt_item.name), {})
	component_rows = [
		{
			"component_type": "Purchase Cost",
			"amount": purchase_cost,
			"reference_doctype": "Purchase Receipt",
			"reference_name": receipt_name,
		}
	]

	additional_total = 0.0
	for account, amounts in account_costs.items():
		account_amount = flt(amounts.get("base_amount") or amounts.get("amount"))
		if not account_amount:
			continue
		additional_total += account_amount
		component_rows.append(
			{
				"component_type": account,
				"amount": account_amount / qty,
				"reference_doctype": "Landed Cost Voucher",
				"notes": "Allocated landed cost",
			}
		)

	total_landed_cost = purchase_cost + (additional_total / qty)
	_update_item_price_and_components(item_code, total_landed_cost, component_rows)


def _update_item_price_and_components(item_code, selling_price, component_rows):
	item_doc = frappe.get_doc("Item", item_code)
	item_doc.set("landed_cost_components", [])
	for row in component_rows:
		item_doc.append("landed_cost_components", row)

	item_doc.flags.ignore_permissions = True
	item_doc.save()

	price_list = _get_standard_selling_price_list()
	if not price_list:
		return

	item_price = frappe.db.get_value(
		"Item Price",
		{"item_code": item_code, "price_list": price_list},
		"name",
	)
	if item_price:
		frappe.db.set_value("Item Price", item_price, "price_list_rate", selling_price)
	else:
		doc = frappe.new_doc("Item Price")
		doc.item_code = item_code
		doc.price_list = price_list
		doc.price_list_rate = selling_price
		doc.insert(ignore_permissions=True)


def _get_standard_selling_price_list():
	standard = frappe.db.get_value("Price List", "Standard Selling", "name")
	if standard:
		return standard

	return frappe.db.get_value("Price List", {"selling": 1, "enabled": 1}, "name")


def _is_imported_item(item_code):
	return bool(frappe.db.get_value("Item", item_code, "is_imported"))
