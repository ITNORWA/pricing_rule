# Copyright (c) 2025, Newton Manyisa and contributors
# For license information, please see license.txt

import frappe


def execute():
	docname = frappe.db.get_value(
		"Pricing Rule User Guide",
		{"title": "Pricing Rule User Guide"},
		"name",
	)

	doc = (
		frappe.get_doc("Pricing Rule User Guide", docname)
		if docname
		else frappe.new_doc("Pricing Rule User Guide")
	)

	doc.title = "Pricing Rule User Guide"
	doc.content = (
		"# Pricing Rule User Guide\n\n"
		"This guide explains how to use the Pricing Rule app. It is written for everyday users, not developers.\n\n"
		"## What this app does\n\n"
		"- Limits discounts by Item Group or specific Items.\n"
		"- Requires approval when discounts exceed the allowed limit.\n"
		"- Updates selling price for imported items using landed cost.\n\n"
		"## Who should use this\n\n"
		"- Sales Users: create quotations and sales orders.\n"
		"- Sales Managers: approve discounts that exceed the limit.\n"
		"- System Managers: maintain rules and guide content.\n\n"
		"## Before you start\n\n"
		"Make sure you have:\n\n"
		"- Access to the **Item Group Discount Rule** list.\n"
		"- Access to **Quotation** or **Sales Order**.\n"
		"- The correct role for approvals (Sales Manager).\n\n"
		"## Create a rule for an Item Group\n\n"
		"Use this when you want the same discount limit for all items in a group.\n\n"
		"1. Go to <a href=\"/app/item-group-discount-rule\">Item Group Discount Rule</a>.\n"
		"2. Click **Add Item Group Discount Rule**.\n"
		"3. Set **Apply On** to **Item Group**.\n"
		"4. Choose the **Item Group**.\n"
		"5. Set **Start Date** and optional **End Date**.\n"
		"6. Set **Maximum Discount Percentage**.\n"
		"7. Click **Reload Items** to pull the group items.\n"
		"8. Remove any items you do not want this rule to apply to.\n"
		"9. Save the rule.\n\n"
		"Notes:\n"
		"- If a group has no items, the list stays empty.\n"
		"- Items you delete from the list stay excluded.\n\n"
		"## Create a rule for specific Items\n\n"
		"Use this when you want a rule for only a few items.\n\n"
		"1. Go to <a href=\"/app/item-group-discount-rule\">Item Group Discount Rule</a>.\n"
		"2. Click **Add Item Group Discount Rule**.\n"
		"3. Set **Apply On** to **Item**.\n"
		"4. Add only the items you want in the **Items** table.\n"
		"5. Set **Start Date**, optional **End Date**, and **Maximum Discount Percentage**.\n"
		"6. Save the rule.\n\n"
		"Notes:\n"
		"- The Items table only shows the items you add.\n\n"
		"## How discount approval works\n\n"
		"- When a discount exceeds the rule limit, the document requires approval.\n"
		"- Quotation and Sales Order will show **Approval Status**.\n"
		"- Sales Managers can approve or return the request.\n\n"
		"### Approval status colors\n\n"
		"- <span style=\"color: var(--blue-500); font-weight: 600;\">Draft</span>\n"
		"- <span style=\"color: var(--orange-500); font-weight: 600;\">Pending Approval</span>\n"
		"- <span style=\"color: var(--green-500); font-weight: 600;\">Approved</span>\n"
		"- <span style=\"color: var(--purple-500); font-weight: 600;\">Submitted</span>\n\n"
		"### Request approval\n\n"
		"1. Save your <a href=\"/app/quotation\">Quotation</a> or <a href=\"/app/sales-order\">Sales Order</a>.\n"
		"2. If approval is required, change status to **Pending Approval** using the workflow action.\n"
		"3. Wait for a Sales Manager to approve.\n\n"
		"### Approve or return\n\n"
		"Sales Managers can open the document and select **Approve** or **Return for Amendment**.\n\n"
		"## Update item discounts on existing items\n\n"
		"If you change a rule and want to update item discounts:\n\n"
		"1. Open the rule.\n"
		"2. Click **Refresh/Update Items**.\n"
		"3. The system updates `max_discount` on items in the rule.\n\n"
		"## Imported items and landed cost\n\n"
		"If an item is marked as **Imported**, the app can update its selling price using landed cost:\n\n"
		"- On <a href=\"/app/purchase-receipt\">Purchase Receipt</a> or <a href=\"/app/landed-cost-voucher\">Landed Cost Voucher</a> submit, the price is recalculated.\n"
		"- You can also click **Recalculate Selling Price** from the <a href=\"/app/item\">Item</a> form.\n\n"
		"## Common questions\n\n"
		"**Q: I do not see the guide in search.**\n"
		"A: Make sure you are logged in and have the **System User** role.\n\n"
		"**Q: An item should not be affected by a rule.**\n"
		"A: Remove it from the rule item list and save. It will stay excluded.\n\n"
		"**Q: Why is approval required?**\n"
		"A: The discount on at least one item is above the allowed limit.\n\n"
		"## Need help?\n\n"
		"Contact your System Manager or Sales Manager for help with rules or approvals.\n"
	)
	doc.version = "1.0"
	doc.save(ignore_permissions=True)
