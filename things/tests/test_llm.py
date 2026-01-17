import os
import unittest
from unittest.mock import MagicMock, patch

import app.config as config
import app.services.llm as llm


class TestLLMProviderSelection(unittest.TestCase):
    def setUp(self):
        self._env_backup = dict(os.environ)

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self._env_backup)
        config.reload_settings()

    def test_openrouter_auto_selected_when_key_present(self):
        os.environ["LLM_PROVIDER"] = "auto"
        os.environ["OPENROUTER_API_KEY"] = "test-key"
        os.environ["OPENROUTER_MODEL"] = "openai/gpt-4o-mini"
        os.environ.pop("OPENAI_API_KEY", None)
        os.environ.pop("LLM_API_KEY", None)
        os.environ.pop("LLM_ENDPOINT", None)

        config.reload_settings()

        with patch.object(llm.openai, "OpenAI") as mock_openai:
            mock_openai.return_value = MagicMock()
            _client, model, provider = llm.get_llm_client_and_model()

        self.assertEqual(provider, "openrouter")
        self.assertEqual(model, "openai/gpt-4o-mini")
        mock_openai.assert_called_once()


    def test_openai_selected_in_auto_when_openai_key_present(self):
        os.environ["LLM_PROVIDER"] = "auto"
        os.environ["OPENAI_API_KEY"] = "test-openai-key"
        os.environ["OPENAI_MODEL"] = "gpt-4o-mini"
        os.environ.pop("OPENROUTER_API_KEY", None)
        os.environ.pop("LLM_API_KEY", None)
        os.environ.pop("LLM_ENDPOINT", None)

        config.reload_settings()

        with patch.object(llm.openai, "OpenAI") as mock_openai:
            mock_openai.return_value = MagicMock()
            _client, model, provider = llm.get_llm_client_and_model()

        self.assertEqual(provider, "openai")
        self.assertEqual(model, "gpt-4o-mini")
        # openai.OpenAI should be instantiated without a custom base_url
        _args, kwargs = mock_openai.call_args
        self.assertIn("api_key", kwargs)
        self.assertNotIn("base_url", kwargs)


if __name__ == "__main__":
    unittest.main()
