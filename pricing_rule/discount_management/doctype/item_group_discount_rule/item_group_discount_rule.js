frappe.ui.form.on("Item Group Discount Rule", {
	onload(frm) {
		setup_apply_on_handlers(frm);
		add_reload_items_button(frm);
	},
	refresh(frm) {
		setup_apply_on_handlers(frm);
		add_reload_items_button(frm);
	},
	apply_on(frm) {
		set_items_query(frm);
		update_items_for_rule(frm, { force: true });
	},
	item_group(frm) {
		set_items_query(frm);
		update_items_for_rule(frm, { force: true });
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
});

function add_reload_items_button(frm) {
	const grid = frm.get_field("items")?.grid;
	if (!grid || grid._reload_button_added) {
		return;
	}

	const label = `${frappe.utils.icon("refresh", "sm")} ${__("Reload Items")}`;
	const $btn = $(`<button class="btn btn-xs btn-secondary" type="button" title="${__("Reload Items")}">
		${label}
	</button>`);

	grid.grid_custom_buttons.append($btn);
	$btn.on("click", () => update_items_for_rule(frm, { force: true }));
	grid._reload_button_added = true;
}

function setup_apply_on_handlers(frm) {
	if (!frm.doc.apply_on) {
		frm.set_value("apply_on", "Item Group");
	}

	set_items_query(frm);
	update_items_for_rule(frm, { force: frm.is_new() });
}

function update_items_for_rule(frm, { force = false } = {}) {
	if (frm.doc.apply_on === "Item Group") {
		if (!frm.doc.item_group) {
			if (force) {
				populate_items_table(frm, []);
			}
			return;
		}
		if (!force) {
			return;
		}
		frm.call("get_items_for_item_group").then((response) => {
			const items = response.message || [];
			populate_items_table(frm, items);
		});
		return;
	}

	if (frm.doc.apply_on === "Item") {
		// Keep only user-selected rows for Item rules.
		return;
	}
}

function populate_items_table(frm, items) {
	if (!items.length) {
		frm.clear_table("items");
		frm.refresh_field("items");
		return;
	}

	const current = (frm.doc.items || []).map((row) => row.item_code);
	const same_length = current.length === items.length;
	const same_items = same_length && items.every((item) => current.includes(item));
	if (same_items) {
		return;
	}

	frm.clear_table("items");
	items.forEach((item_code) => {
		const row = frm.add_child("items");
		row.item_code = item_code;
	});
	frm.refresh_field("items");
}

function set_items_query(frm) {
	const grid = frm.get_field("items")?.grid;
	if (!grid) {
		return;
	}

	const item_field = grid.get_field("item_code");
	item_field.get_query = function () {
		if (frm.doc.apply_on === "Item Group") {
			if (!frm.doc.item_group) {
				return { filters: { name: ["=", ""] } };
			}
			return { filters: { item_group: frm.doc.item_group } };
		}

		return {};
	};
}
