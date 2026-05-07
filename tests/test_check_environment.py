import importlib.util
import os
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]


def load_check_environment():
    module_path = ROOT / "scripts" / "check_environment.py"
    spec = importlib.util.spec_from_file_location("check_environment", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CheckEnvironmentTest(unittest.TestCase):
    def setUp(self):
        self.mod = load_check_environment()

    def test_collect_status_reports_missing_api_config(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            status = self.mod.collect_status(base_url="", api_key="")

        self.assertFalse(status["ready"])
        self.assertFalse(status["base_url_configured"])
        self.assertFalse(status["api_key_configured"])
        self.assertIn("GPT_IMAGE_2_BASE_URL", self.mod.configuration_help())
        self.assertIn("BASE_URL_API_KEY", self.mod.configuration_help())

    def test_collect_status_accepts_explicit_config(self):
        status = self.mod.collect_status(
            base_url="https://api.example.com",
            api_key="test-key",
        )

        self.assertTrue(status["base_url_configured"])
        self.assertTrue(status["api_key_configured"])

    def test_collect_status_reads_new_environment_names(self):
        with mock.patch.dict(
            os.environ,
            {
                "GPT_IMAGE_2_BASE_URL": "https://api.example.com",
                "BASE_URL_API_KEY": "test-key",
            },
            clear=True,
        ):
            status = self.mod.collect_status()

        self.assertTrue(status["ready"])


if __name__ == "__main__":
    unittest.main()
