import unittest
from unittest.mock import MagicMock
from app.rag.query_transform import (
    rewrite_query,
    generate_multi_queries,
    generate_hyde_document,
    generate_step_back_query,
    decompose_query,
    QueryTransformer,
)


class TestQueryTransform(unittest.TestCase):

    def test_rewrite_query(self):
        mock_client = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = "insufficient funds payment retry policy"
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        result = rewrite_query(
            "What do I do when card has no money?",
            merchant_id="techstore",
            client=mock_client,
        )
        self.assertEqual(result, "insufficient funds payment retry policy")
        mock_client.chat.completions.create.assert_called_once()

    def test_generate_multi_queries(self):
        mock_client = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = "insufficient funds retry schedule\ncustomer notification policy\nfailure escalation"
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        original_query = "Payment failed"
        queries = generate_multi_queries(
            original_query,
            num_queries=3,
            client=mock_client,
        )
        self.assertIn(original_query, queries)
        self.assertIn("insufficient funds retry schedule", queries)
        self.assertGreaterEqual(len(queries), 3)

    def test_generate_hyde_document(self):
        mock_client = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = "For insufficient funds, the system retries after 24 hours up to 3 times."
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        result = generate_hyde_document("What is the policy?", client=mock_client)
        self.assertIn("retries after 24 hours", result)

    def test_generate_step_back_query(self):
        mock_client = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = "What are the standard payment retry mechanisms?"
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        result = generate_step_back_query("Why did card 123 fail?", client=mock_client)
        self.assertEqual(result, "What are the standard payment retry mechanisms?")

    def test_decompose_query(self):
        mock_client = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = "What is the retry schedule?\nHow to notify customer?"
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        result = decompose_query("How to retry and notify customer?", client=mock_client)
        self.assertEqual(len(result), 2)
        self.assertIn("What is the retry schedule?", result)

    def test_query_transformer_class(self):
        mock_client = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = "rewritten search query"
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        transformer = QueryTransformer(client=mock_client)
        res = transformer.transform("raw query", strategy="rewrite")
        self.assertEqual(res, "rewritten search query")

        passthrough = transformer.transform("raw query", strategy="passthrough")
        self.assertEqual(passthrough, "raw query")


if __name__ == "__main__":
    unittest.main()
