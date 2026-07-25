import os
import unittest

from backend.app.core.config import Settings, sync_environment


class SyncEnvironmentTests(unittest.TestCase):
    """A key supplied only through .env must reach the AI modules.

    The feature modules read os.getenv directly, while pydantic-settings loads
    .env onto the Settings object without touching the process environment.
    """

    def setUp(self):
        self._saved = {
            name: os.environ.get(name)
            for name in ("GEMINI_API_KEY", "GEMINI_MODEL", "EDUGENIE_USE_LOCAL_MODEL")
        }

    def tearDown(self):
        for name, value in self._saved.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value

    def test_gemini_key_is_published_to_process_environment(self):
        os.environ.pop("GEMINI_API_KEY", None)
        settings = Settings(gemini_api_key="key-from-dotenv", gemini_model="gemini-1.5-pro")

        sync_environment(settings)

        self.assertEqual(os.getenv("GEMINI_API_KEY"), "key-from-dotenv")
        self.assertEqual(os.getenv("GEMINI_MODEL"), "gemini-1.5-pro")

    def test_ai_client_reads_the_synced_key(self):
        from backend.app.ai_modules.features.ai_client import GeminiConfig

        os.environ.pop("GEMINI_API_KEY", None)
        sync_environment(Settings(gemini_api_key="key-from-dotenv"))

        self.assertEqual(GeminiConfig.from_env().api_key, "key-from-dotenv")

    def test_disabled_local_model_is_published_as_zero(self):
        sync_environment(Settings(edugenie_use_local_model=False))

        self.assertEqual(os.getenv("EDUGENIE_USE_LOCAL_MODEL"), "0")

    def test_missing_key_does_not_create_empty_variable(self):
        os.environ.pop("GEMINI_API_KEY", None)

        sync_environment(Settings(gemini_api_key=None))

        self.assertIsNone(os.getenv("GEMINI_API_KEY"))


if __name__ == "__main__":
    unittest.main()
