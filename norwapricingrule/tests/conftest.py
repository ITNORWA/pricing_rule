import sys
from types import ModuleType

# Create base mock frappe module
mock_frappe = ModuleType("frappe")

# Mock frappe.tests.utils.FrappeTestCase
mock_tests = ModuleType("tests")
mock_utils = ModuleType("utils")

class FrappeTestCase:
    pass

mock_utils.FrappeTestCase = FrappeTestCase
mock_tests.utils = mock_utils
mock_frappe.tests = mock_tests

# Other mocks your code needs
mock_frappe.db = ModuleType("db")
mock_frappe.get_doc = lambda *args, **kwargs: None
mock_frappe.utils = ModuleType("utils")
mock_frappe.utils.flt = float

# Register the mock
sys.modules["frappe"] = mock_frappe
