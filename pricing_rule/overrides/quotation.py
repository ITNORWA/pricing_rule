from erpnext.selling.doctype.quotation.quotation import Quotation as ERPNextQuotation


class Quotation(ERPNextQuotation):
	def validate_max_discount(self):
		# Skip core enforcement; handled by pricing_rule approval flow.
		return
