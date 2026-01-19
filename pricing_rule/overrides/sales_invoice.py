from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice as ERPNextSalesInvoice


class SalesInvoice(ERPNextSalesInvoice):
	def validate_max_discount(self):
		# Skip core enforcement; approval handled in Quotation/Sales Order only.
		return
