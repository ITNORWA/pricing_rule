from erpnext.selling.doctype.sales_order.sales_order import SalesOrder as ERPNextSalesOrder


class SalesOrder(ERPNextSalesOrder):
	def validate_max_discount(self):
		# Skip core enforcement; handled by pricing_rule approval flow.
		return
