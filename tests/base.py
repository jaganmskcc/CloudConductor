import os
from importlib.machinery import SourceFileLoader
from unittest import TestCase


class CloudConductorTest(TestCase):
    TESTS_DIR = os.path.dirname(__file__)

    def setUp(self):
        cc = SourceFileLoader(
            "CloudConductor",
            os.path.join(os.path.dirname(self.TESTS_DIR), "CloudConductor")
        ).load_module()
        cc.configure_import_paths()
