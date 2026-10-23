import unittest

import warehouse_robot_diagnostics


class TestPackage(unittest.TestCase):
    def test_package_imports(self):
        self.assertIsNotNone(warehouse_robot_diagnostics.__doc__)
