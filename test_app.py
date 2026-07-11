import unittest
from unittest.mock import patch, MagicMock
import json
import os
from app import app, extract_video_id

class YouTubeSummarizerTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        self.old_key = os.environ.get("GEMINI_API_KEY")
        os.environ["GEMINI_API_KEY"] = "mock_api_key"

    def tearDown(self):
        if self.old_key is not None:
            os.environ["GEMINI_API_KEY"] = self.old_key
        else:
            os.environ.pop("GEMINI_API_KEY", None)

    def test_extract_video_id(self):
        """Test robust YouTube video ID extraction."""
        valid_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "http://youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://www.youtube.com/embed/dQw4w9WgXcQ",
            "https://youtube.com/live/dQw4w9WgXcQ?feature=share",
            "https://m.youtube.com/watch?v=dQw4w9WgXcQ",
            "dQw4w9WgXcQ" # Raw ID
        ]
        for url in valid_urls:
            self.assertEqual(extract_video_id(url), "dQw4w9WgXcQ")

        invalid_urls = [
            "https://www.google.com",
            "https://youtube.com",
            "",
            None
        ]
        for url in invalid_urls:
            self.assertIsNone(extract_video_id(url))

    def test_serve_index(self):
        """Test index page returns successfully."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_config_check(self):
        """Test configuration check response."""
        response = self.client.get('/api/config-check')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('configured', data)
        self.assertTrue(data['configured'])

    def test_summarize_missing_url(self):
        """Test error when no URL is provided."""
        response = self.client.post('/api/summarize', 
                                    data=json.dumps({}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_summarize_invalid_url(self):
        """Test error for invalid YouTube URLs."""
        response = self.client.post('/api/summarize', 
                                    data=json.dumps({"url": "https://google.com"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    @patch('app.fetch_youtube_transcript')
    @patch('google.generativeai.GenerativeModel')
    def test_summarize_success_mock(self, mock_gen_model, mock_fetch_transcript):
        """Test successful end-to-end mock AI summarization."""
        # 1. Mock Transcript Fetch
        mock_fetch_transcript.return_value = ("Hello world transcript content for testing. This is a longer mock transcript that has more than fifty characters to pass validation checks.", None)

        # 2. Mock Gemini API generate_content
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            "summary": "This is a mock AI summary.",
            "key_points": [
                "**Mock Point 1**: Details about point 1.",
                "**Mock Point 2**: Details about point 2."
            ],
            "takeaway": "This is a mock final takeaway."
        })
        
        mock_model_instance = MagicMock()
        mock_model_instance.generate_content.return_value = mock_response
        mock_gen_model.return_value = mock_model_instance

        # 3. Post request to test
        response = self.client.post('/api/summarize', 
                                    data=json.dumps({"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}),
                                    content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertEqual(data["videoId"], "dQw4w9WgXcQ")
        self.assertEqual(data["summary"], "This is a mock AI summary.")
        self.assertEqual(len(data["key_points"]), 2)
        self.assertEqual(data["takeaway"], "This is a mock final takeaway.")

if __name__ == '__main__':
    unittest.main()
