function setupDiscountApprovalButtons(frm) {
	if (frm.is_new() || frm.doc.docstatus !== 0) {
		return;
	}

	if (frm.doc.approval_status === "Pending Approval") {
		frm.page.set_indicator("Pending Approval", "orange");
	} else if (frm.doc.approval_status === "Approved") {
		frm.page.set_indicator("Approved", "green");
	} else if (frm.doc.approval_status === "Submitted") {
		frm.page.set_indicator("Submitted", "blue");
	}
}

frappe.ui.form.on("Sales Order", {
	refresh(frm) {
		setupDiscountApprovalButtons(frm);
	},
});
