import base64
import http.server
import importlib.util
import json
import socketserver
import threading
import tempfile
import unittest
from unittest import mock
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_generate_image():
    module_path = ROOT / "scripts" / "generate_image.py"
    spec = importlib.util.spec_from_file_location("generate_image", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class GenerateImageHelpersTest(unittest.TestCase):
    def setUp(self):
        self.mod = load_generate_image()

    def test_api_url_handles_base_urls_with_or_without_v1(self):
        self.assertEqual(
            self.mod.api_url("https://api.example.com", "generations"),
            "https://api.example.com/v1/images/generations",
        )
        self.assertEqual(
            self.mod.api_url("https://api.example.com/v1", "edits"),
            "https://api.example.com/v1/images/edits",
        )

    def test_generation_payload_includes_output_controls_and_omits_none(self):
        payload = self.mod.build_image_payload(
            model="gpt-image-2",
            prompt="draw a cat",
            size="1024x1024",
            quality="auto",
            output_format="png",
            output_compression=None,
            moderation="low",
            response_format=None,
        )
        self.assertEqual(payload["output_format"], "png")
        self.assertEqual(payload["moderation"], "low")
        self.assertNotIn("output_compression", payload)
        self.assertNotIn("response_format", payload)

    def test_parse_args_reads_new_environment_names(self):
        with mock.patch.dict(
            "os.environ",
            {
                "GPT_IMAGE_2_BASE_URL": "https://api.example.com",
                "BASE_URL_API_KEY": "test-key",
            },
            clear=True,
        ):
            args = self.mod.parse_args(["--prompt", "draw a cat"])

        self.assertEqual(args.base_url, "https://api.example.com")
        self.assertEqual(args.api_key, "test-key")

    def test_extract_image_bytes_decodes_b64_json(self):
        expected = b"png-bytes"
        response = {"data": [{"b64_json": base64.b64encode(expected).decode()}]}
        self.assertEqual(self.mod.extract_image_bytes(response, timeout=1), expected)

    def test_multipart_body_uses_image_array_and_mask_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            image_a = tmp_path / "a.png"
            image_b = tmp_path / "b.png"
            mask = tmp_path / "mask.png"
            image_a.write_bytes(b"a")
            image_b.write_bytes(b"b")
            mask.write_bytes(b"m")

            body, content_type = self.mod.build_edit_multipart(
                fields={"model": "gpt-image-2", "prompt": "edit"},
                images=[str(image_a), str(image_b)],
                mask=str(mask),
                timeout=1,
            )

        text = body.decode("utf-8", errors="ignore")
        self.assertIn("multipart/form-data; boundary=", content_type)
        self.assertEqual(text.count('name="image[]"'), 2)
        self.assertIn('name="mask"', text)

    def test_request_json_retries_retryable_http_status(self):
        image_bytes = b"image"

        class Handler(http.server.BaseHTTPRequestHandler):
            attempts = 0

            def do_POST(self):
                Handler.attempts += 1
                self.rfile.read(int(self.headers.get("Content-Length", "0")))
                if Handler.attempts == 1:
                    self.send_response(500)
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "try again"}).encode())
                    return

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(
                    json.dumps(
                        {
                            "data": [
                                {
                                    "b64_json": base64.b64encode(
                                        image_bytes
                                    ).decode()
                                }
                            ]
                        }
                    ).encode()
                )

            def log_message(self, format, *args):
                return

        with socketserver.TCPServer(("127.0.0.1", 0), Handler) as server:
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                response = self.mod.request_json(
                    url=f"http://127.0.0.1:{server.server_address[1]}/v1/images/generations",
                    payload={"prompt": "cat"},
                    api_key="test-key",
                    timeout=2,
                    retries=1,
                    retry_delay=0,
                )
            finally:
                server.shutdown()
                thread.join(timeout=2)

        self.assertEqual(Handler.attempts, 2)
        self.assertEqual(self.mod.extract_image_bytes(response, timeout=1), image_bytes)


if __name__ == "__main__":
    unittest.main()
