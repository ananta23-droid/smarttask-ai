import os
import unittest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from app.schemas.task import AISummarizeRequestItem, AISummarizeResponse
from app.models.task import TaskPriority, TaskStatus
from app.services.ai_service import summarize_tasks_with_ai


class TestOpenRouterMigration(unittest.TestCase):
    def setUp(self):
        self.sample_tasks = [
            AISummarizeRequestItem(
                title="Prepare DBMS presentation",
                description="Slides on indexing and query optimization",
                priority=TaskPriority.HIGH,
                status=TaskStatus.TODO
            ),
            AISummarizeRequestItem(
                title="Review pull requests",
                description="Frontend refactoring PR",
                priority=TaskPriority.MEDIUM,
                status=TaskStatus.IN_PROGRESS
            ),
            AISummarizeRequestItem(
                title="Update documentation",
                description="API endpoints update",
                priority=TaskPriority.LOW,
                status=TaskStatus.COMPLETED
            )
        ]

    def test_missing_api_key(self):
        """Test that missing OPENROUTER_API_KEY raises HTTP 503 with clear message."""
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": ""}, clear=False):
            with self.assertRaises(HTTPException) as ctx:
                summarize_tasks_with_ai(self.sample_tasks)
            self.assertEqual(ctx.exception.status_code, 503)
            self.assertIn("OpenRouter API key is not configured", ctx.exception.detail)
            self.assertIn("OPENROUTER_API_KEY", ctx.exception.detail)

    def test_empty_task_list(self):
        """Test that empty task list returns standard response without calling API."""
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "fake-key"}, clear=False):
            result = summarize_tasks_with_ai([])
            self.assertIsInstance(result, AISummarizeResponse)
            self.assertEqual(result.summary, "You currently have 0 tasks in your list.")
            self.assertEqual(result.highest_priority_tasks, [])
            self.assertEqual(result.recommended_order, [])
            self.assertIn("empty", result.recommendation.lower())

    @patch("app.services.ai_service.httpx.Client")
    def test_successful_openrouter_response(self, mock_httpx_client_cls):
        """Test successful structured response handling from OpenRouter."""
        mock_httpx_client = MagicMock()
        mock_httpx_client_cls.return_value.__enter__.return_value = mock_httpx_client

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": (
            '{"summary": "You have 3 tasks. 1 is high priority.", '
            '"highest_priority_tasks": ["Prepare DBMS presentation"], '
            '"recommended_order": ["Prepare DBMS presentation", "Review pull requests", "Update documentation"], '
            '"recommendation": "Focus on the high-priority DBMS presentation first."}'
            )}}]
        }
        mock_httpx_client.post.return_value = mock_response

        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key-123", "OPENROUTER_MODEL": "google/gemini-2.5-flash"}, clear=False):
            result = summarize_tasks_with_ai(self.sample_tasks)

            self.assertIsInstance(result, AISummarizeResponse)
            self.assertEqual(result.summary, "You have 3 tasks. 1 is high priority.")
            self.assertEqual(result.highest_priority_tasks, ["Prepare DBMS presentation"])
            self.assertEqual(len(result.recommended_order), 3)
            self.assertEqual(result.recommended_order[0], "Prepare DBMS presentation")
            self.assertIn("DBMS", result.recommendation)

            mock_httpx_client.post.assert_called_once()
            call_kwargs = mock_httpx_client.post.call_args.kwargs
            self.assertEqual(call_kwargs["json"]["model"], "google/gemini-2.5-flash")
            self.assertIn("Authorization", call_kwargs["headers"])

    @patch("app.services.ai_service.httpx.Client")
    def test_invalid_api_key_error(self, mock_httpx_client_cls):
        """Test that OpenRouter auth error raises HTTP 401."""
        mock_httpx_client = MagicMock()
        mock_httpx_client_cls.return_value.__enter__.return_value = mock_httpx_client
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"error": {"message": "Unauthorized"}}
        mock_httpx_client.post.return_value = mock_response

        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "invalid-key"}, clear=False):
            with self.assertRaises(HTTPException) as ctx:
                summarize_tasks_with_ai(self.sample_tasks)
            self.assertEqual(ctx.exception.status_code, 401)
            self.assertIn("OpenRouter authentication failed", ctx.exception.detail)

    @patch("app.services.ai_service.httpx.Client")
    def test_rate_limit_quota_error(self, mock_httpx_client_cls):
        """Test that OpenRouter 429 quota error raises HTTP 429."""
        mock_httpx_client = MagicMock()
        mock_httpx_client_cls.return_value.__enter__.return_value = mock_httpx_client
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.json.return_value = {"error": {"message": "Quota exceeded"}}
        mock_httpx_client.post.return_value = mock_response

        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}, clear=False):
            with self.assertRaises(HTTPException) as ctx:
                summarize_tasks_with_ai(self.sample_tasks)
            self.assertEqual(ctx.exception.status_code, 429)
            self.assertIn("OpenRouter rate limit or quota exceeded", ctx.exception.detail)

    @patch("app.services.ai_service.httpx.Client")
    def test_malformed_json_response(self, mock_httpx_client_cls):
        """Test that malformed JSON response from OpenRouter is handled gracefully with 502."""
        mock_httpx_client = MagicMock()
        mock_httpx_client_cls.return_value.__enter__.return_value = mock_httpx_client
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "This is not json at all"}}]
        }
        mock_httpx_client.post.return_value = mock_response

        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}, clear=False):
            with self.assertRaises(HTTPException) as ctx:
                summarize_tasks_with_ai(self.sample_tasks)
            self.assertEqual(ctx.exception.status_code, 502)
            self.assertIn("Failed to parse structured JSON response from OpenRouter", ctx.exception.detail)

    @patch("app.services.ai_service.httpx.Client")
    def test_payment_required_error(self, mock_httpx_client_cls):
        """Test that OpenRouter 402 credit/token error raises HTTP 402."""
        mock_httpx_client = MagicMock()
        mock_httpx_client_cls.return_value.__enter__.return_value = mock_httpx_client
        mock_response = MagicMock()
        mock_response.status_code = 402
        mock_response.json.return_value = {"error": {"message": "Requires more credits"}}
        mock_httpx_client.post.return_value = mock_response

        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}, clear=False):
            with self.assertRaises(HTTPException) as ctx:
                summarize_tasks_with_ai(self.sample_tasks)
            self.assertEqual(ctx.exception.status_code, 402)
            self.assertIn("OpenRouter payment or credits required", ctx.exception.detail)

    @patch("app.services.ai_service.httpx.Client")
    def test_model_not_found_error(self, mock_httpx_client_cls):
        """Test that OpenRouter 404 model not found error raises HTTP 502 with model name."""
        mock_httpx_client = MagicMock()
        mock_httpx_client_cls.return_value.__enter__.return_value = mock_httpx_client
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"error": {"message": "Model not found"}}
        mock_httpx_client.post.return_value = mock_response

        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key", "OPENROUTER_MODEL": "google/gemini-2.5-flash"}, clear=False):
            with self.assertRaises(HTTPException) as ctx:
                summarize_tasks_with_ai(self.sample_tasks)
            self.assertEqual(ctx.exception.status_code, 502)
            self.assertIn("Configured OpenRouter model 'google/gemini-2.5-flash' was not found", ctx.exception.detail)

    @patch("app.services.ai_service.httpx.Client")
    def test_network_connection_error(self, mock_httpx_client_cls):
        """Test that network connection errors raise HTTP 502 with user-friendly message."""
        mock_httpx_client = MagicMock()
        mock_httpx_client_cls.return_value.__enter__.return_value = mock_httpx_client
        import httpx
        mock_httpx_client.post.side_effect = httpx.ConnectError("Connection refused")

        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}, clear=False):
            with self.assertRaises(HTTPException) as ctx:
                summarize_tasks_with_ai(self.sample_tasks)
            self.assertEqual(ctx.exception.status_code, 502)
            self.assertIn("Could not connect to OpenRouter servers", ctx.exception.detail)


if __name__ == "__main__":
    unittest.main()
