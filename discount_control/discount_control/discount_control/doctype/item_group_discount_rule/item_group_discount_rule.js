// This adds a button to the Item Group Discount Rule form
frappe.ui.form.on('Item Group Discount Rule', {
    refresh: function(frm) {
        if (!frm.doc.__islocal) {
            frm.add_custom_button(__('Apply Rule to Draft Orders'), function() {
                frappe.call({
                    method: "discount_control.discount_control.doctype.item_group_discount_rule.item_group_discount_rule.apply_to_drafts",
                    args: {
                        rule_name: frm.doc.name,
                        item_group: frm.doc.item_group
                    },
                    callback: function(r) {
                        if(!r.exc) {
                            frappe.msgprint("Draft Sales Orders updated successfully.");
                        }
                    }
                });
            });
        }
    }
});