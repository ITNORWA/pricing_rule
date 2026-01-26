import frappe
from frappe.model.document import Document
from frappe.model.naming import append_number_if_name_exists


class ItemGroupDiscountRule(Document):
	def autoname(self):
		if self.apply_on == "Item Group":
			base_name = self.item_group or "Item Group"
		elif self.apply_on == "Item":
			base_name = "Items"
		else:
			base_name = "Items"

		self.name = append_number_if_name_exists(self.doctype, base_name)

	def before_insert(self):
		if not self.created_by:
			self.created_by = frappe.session.user

	def validate(self):
		self._validate_dates()
		self._validate_unique_item_group()
		self.last_modified_date = frappe.utils.now_datetime()

	def _validate_dates(self):
		if not self.start_date:
			frappe.throw("Start Date is required.")

		if self.end_date and self.end_date < self.start_date:
			frappe.throw("End Date cannot be before Start Date.")

	def _validate_unique_item_group(self):
		if self.apply_on != "Item Group" or not self.item_group:
			return

		existing = frappe.db.get_value(
			"Item Group Discount Rule",
			{
				"item_group": self.item_group,
				"apply_on": "Item Group",
				"name": ["!=", self.name],
			},
			"name",
		)
		if existing:
			frappe.throw(f"Discount rule already exists for item group {self.item_group}.")

	@frappe.whitelist()
	def refresh_update_items(self):
		item_names = _get_rule_item_codes(self)
		if not item_names:
			return "No items found for this rule."

		frappe.db.set_value(
			"Item",
			{"name": ["in", item_names]},
			"max_discount",
			self.max_discount_percentage or 0,
		)
		return f"Updated max discount for {len(item_names)} items in {self.item_group}."

	@frappe.whitelist()
	def get_items_for_item_group(self):
		if not self.item_group:
			return []

		return frappe.get_all(
			"Item",
			filters={"item_group": self.item_group},
			pluck="name",
		)

	@frappe.whitelist()
	def get_all_items(self):
		return frappe.get_all("Item", pluck="name")

	@frappe.whitelist()
	def toggle_rule(self):
		self.is_enabled = 0 if self.is_enabled else 1
		self.save(ignore_permissions=True)
		return "Rule enabled." if self.is_enabled else "Rule disabled."


def _get_rule_item_codes(rule_doc):
	if rule_doc.apply_on == "Item Group":
		if not rule_doc.item_group:
			return []
		item_codes = [row.item_code for row in rule_doc.items if row.item_code]
		if item_codes:
			return item_codes

		return frappe.get_all(
			"Item",
			filters={"item_group": rule_doc.item_group},
			pluck="name",
		)

	if rule_doc.apply_on == "Item":
		return [row.item_code for row in rule_doc.items if row.item_code]

	return []
