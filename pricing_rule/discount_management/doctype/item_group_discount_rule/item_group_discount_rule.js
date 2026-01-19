frappe.ui.form.on("Item Group Discount Rule", {
	onload(frm) {
		setup_apply_on_handlers(frm);
	},
	refresh(frm) {
		setup_apply_on_handlers(frm);
	},
	apply_on(frm) {
		update_items_for_rule(frm);
	},
	item_group(frm) {
		update_items_for_rule(frm);
	},
	refresh_update_items(frm) {
		if (!frm.doc.item_group) {
			frappe.msgprint("Please select an Item Group first.");
			return;
		}

		frm.call("refresh_update_items").then((response) => {
			if (response && response.message) {
				frappe.msgprint(response.message);
			}
		});
	},
	toggle_rule(frm) {
		frm.call("toggle_rule").then((response) => {
			if (response && response.message) {
				frappe.msgprint(response.message);
			}
			frm.reload_doc();
		});
	},
});

function setup_apply_on_handlers(frm) {
	if (!frm.doc.apply_on) {
		frm.set_value("apply_on", "Item Group");
	}

	update_items_for_rule(frm);
}

function update_items_for_rule(frm) {
	if (frm.doc.apply_on === "Item Group") {
		if (!frm.doc.item_group) {
			return;
		}
		frm.call("get_items_for_item_group").then((response) => {
			const items = response.message || [];
			populate_items_table(frm, items);
		});
		return;
	}

	if (frm.doc.apply_on === "Item") {
		frm.call("get_all_items").then((response) => {
			const items = response.message || [];
			populate_items_table(frm, items);
		});
	}
}

function populate_items_table(frm, items) {
	const current = (frm.doc.items || []).map((row) => row.item_code);
	const missing = items.filter((item) => !current.includes(item));
	if (!missing.length && current.length) {
		return;
	}

	frm.clear_table("items");
	items.forEach((item_code) => {
		const row = frm.add_child("items");
		row.item_code = item_code;
	});
	frm.refresh_field("items");
}
