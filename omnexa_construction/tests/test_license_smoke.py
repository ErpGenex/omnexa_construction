from frappe.tests.utils import FrappeTestCase

from omnexa_construction import hooks, license_gate


class TestConstructionLicenseSmoke(FrappeTestCase):
	def test_license_gate_is_wired(self):
		self.assertEqual(hooks.before_request, ["omnexa_construction.license_gate.before_request"])
		self.assertEqual(license_gate._APP, "omnexa_construction")
