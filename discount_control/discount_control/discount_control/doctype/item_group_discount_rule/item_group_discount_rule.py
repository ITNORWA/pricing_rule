import frappe
from frappe.model.document import Document

class ItemGroupDiscountRule(Document):
    def validate(self):
        if self.max_discount_percentage < 0 or self.max_discount_percentage > 100:
            frappe.throw("Discount percentage must be between 0 and 100")

@frappe.whitelist()
def apply_to_drafts(rule_name, item_group):
    # 1. Find all Draft Sales Orders containing items from this Item Group
    # This is a bit complex SQL, so we will keep it simple: 
    # Find all Draft Sales Orders, trigger their save.
    
    orders = frappe.db.sql("""
        SELECT distinct parent 
        FROM `tabSales Order Item` 
        WHERE item_group = %s 
        AND docstatus = 0
    """, (item_group), as_dict=True)
    
    count = 0
    for row in orders:
        doc = frappe.get_doc("Sales Order", row.parent)
        # This triggers the 'validate' event we wrote in sales_order_check.py
        doc.save() 
        count += 1
        
    return count