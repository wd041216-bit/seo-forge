#!/usr/bin/env python3
"""GLM-OCR inference server for image content verification.

Serves a lightweight HTTP API on port 8190 for the seo-forge pipeline.
Uses the zai-org/GLM-OCR model from HuggingFace with transformers.

Usage:
    python glm_ocr_server.py [--port 8190] [--model zai-org/GLM-OCR]

API endpoints:
    GET  /health          → {"status": "ok", "model": "GLM-OCR"}
    POST /v1/chat/completions → OpenAI-compatible chat completions with vision
"""

import argparse
import base64
import json
import os
import socketserver
import tempfile
from http.server import HTTPServer, BaseHTTPRequestHandler

import torch
from transformers import AutoProcessor, AutoModelForImageTextToText

MODEL = None
PROCESSOR = None


def load_model(model_name):
    global MODEL, PROCESSOR
    print(f"Loading model: {model_name}...")
    PROCESSOR = AutoProcessor.from_pretrained(model_name, trust_remote_code=True)
    MODEL = AutoModelForImageTextToText.from_pretrained(
        model_name,
        trust_remote_code=True,
        torch_dtype=torch.float16,
        device_map="auto",
    )
    MODEL.eval()
    print(f"Model loaded on {next(MODEL.parameters()).device}")


class OCRHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self._json_response({"status": "ok", "model": "GLM-OCR"})
        else:
            self._json_response({"error": "not found"}, 404)

    def do_POST(self):
        if self.path != "/v1/chat/completions":
            self._json_response({"error": "not found"}, 404)
            return

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            self._json_response({"error": "invalid JSON"}, 400)
            return

        messages = data.get("messages", [])
        if not messages:
            self._json_response({"error": "no messages"}, 400)
            return

        chat_messages = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if isinstance(content, str):
                chat_messages.append({"role": role, "content": [{"type": "text", "text": content}]})
            elif isinstance(content, list):
                processed = []
                for part in content:
                    if part.get("type") == "text":
                        processed.append({"type": "text", "text": part["text"]})
                    elif part.get("type") == "image_url":
                        img_url = part["image_url"]["url"]
                        img_path = self._save_image(img_url)
                        processed.append({"type": "image", "url": img_path})
                chat_messages.append({"role": role, "content": processed})

        if not chat_messages:
            self._json_response({"error": "empty messages"}, 400)
            return

        result = self._run_ocr(chat_messages)
        self._json_response({
            "id": "glm-ocr",
            "object": "chat.completion",
            "choices": [{
                "index": 0,
                "message": {"role": "assistant", "content": result},
                "finish_reason": "stop",
            }],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        })

    def _save_image(self, url_or_data):
        if url_or_data.startswith("data:"):
            header, b64 = url_or_data.split(",", 1)
            ext = "png" if "png" in header else "jpg"
            tmp = tempfile.NamedTemporaryFile(suffix=f".{ext}", delete=False)
            tmp.write(base64.b64decode(b64))
            tmp.close()
            return tmp.name
        elif url_or_data.startswith("/") and os.path.exists(url_or_data):
            return url_or_data
        else:
            import urllib.request
            tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
            urllib.request.urlretrieve(url_or_data, tmp.name)
            tmp.close()
            return tmp.name

    def _run_ocr(self, messages):
        try:
            inputs = PROCESSOR.apply_chat_template(
                messages,
                tokenize=True,
                add_generation_prompt=True,
                return_dict=True,
                return_tensors="pt",
            ).to(MODEL.device)
            inputs.pop("token_type_ids", None)

            with torch.no_grad():
                output_ids = MODEL.generate(**inputs, max_new_tokens=4096)

            output_text = PROCESSOR.decode(
                output_ids[0][inputs["input_ids"].shape[1]:],
                skip_special_tokens=False,
            )
            return output_text.strip()
        except Exception as e:
            print(f"[GLM-OCR] Inference error: {e}")
            return f"ERROR: {e}"

    def _json_response(self, data, code=200):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def log_message(self, format, *args):
        print(f"[GLM-OCR] {args[0]}" if args else "")


def main():
    parser = argparse.ArgumentParser(description="GLM-OCR inference server")
    parser.add_argument("--port", type=int, default=8190, help="Port to serve on")
    parser.add_argument("--model", default="zai-org/GLM-OCR", help="HuggingFace model ID or local path")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind")
    args = parser.parse_args()

    load_model(args.model)

    class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
        daemon_threads = True

    server = ThreadedHTTPServer((args.host, args.port), OCRHandler)
    print(f"GLM-OCR server running at http://{args.host}:{args.port}")
    print("  GET  /health            - Health check")
    print("  POST /v1/chat/completions - Vision OCR (OpenAI-compatible)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.server_close()


if __name__ == "__main__":
    main()