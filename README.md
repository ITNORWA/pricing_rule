# Pricing Rule

Custom discount management app for ERPNext.

This app provides:
- Discount approval workflow for Quotation and Sales Order.
- Item Group / Item specific discount rules.
- Landed cost based selling price updates for imported items.

## Key Features

### Discount Approval Workflow
- Adds custom fields to Quotation and Sales Order:
  - `approval_status`
  - `approval_comments`
  - `requires_discount_approval`
- Custom workflows enforce approval when discount limits are exceeded.
- ERPNext core max discount validation is bypassed in favor of this flow.

### Item Group Discount Rules
- Doctype: **Item Group Discount Rule**
- Apply rules by:
  - Item Group (auto-populates items from a group)
  - Item (manual selection only)
- Rules define a maximum discount percentage.
- Manual deletions in the items list are preserved.

### Imported Item Landed Cost Pricing
- Adds `Item.is_imported` and a `Landed Cost Components` child table.
- On Purchase Receipt or Landed Cost Voucher submission:
  - Calculates landed cost per imported item.
  - Updates or creates Item Price in the standard selling price list.

## App Structure

### Hooks and Overrides
- `pricing_rule/hooks.py`
  - Registers doctypes, events, JS, and overrides.
- `pricing_rule/overrides/quotation.py`
- `pricing_rule/overrides/sales_order.py`
- `pricing_rule/overrides/sales_invoice.py`

### Discount Logic
- `pricing_rule/discount_management/discount_approval.py`
  - Approval workflow logic, validations, and API endpoints.
- `pricing_rule/discount_management/discount_rules.py`
  - Applies max discount to Item based on active rules.
- `pricing_rule/discount_management/doctype/item_group_discount_rule/`
  - Item Group Discount Rule doctype, controller, and client JS.

### Landed Cost Logic
- `pricing_rule/discount_management/landed_cost.py`
  - Recalculates selling price for imported items.

### Fixtures
- `pricing_rule/fixtures/custom_field.json`
- `pricing_rule/fixtures/workflow.json`
- `pricing_rule/fixtures/workflow_state.json`
- `pricing_rule/fixtures/workflow_action_master.json`

## Installation

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch develop
bench install-app pricing_rule
```

## Development

This app uses `pre-commit` for code formatting and linting.

```bash
cd apps/pricing_rule
pre-commit install
```

Enabled tools:
- ruff
- eslint
- prettier
- pyupgrade

## License

MIT
