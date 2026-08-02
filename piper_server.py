import json
import os
import wave
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from piper.voice import PiperVoice

BASE_DIR = r"D:\Bachelorarbeit\Backend_Bachelor"
MODEL_PATH = os.path.join(BASE_DIR, "voices", "en_US-amy-medium.onnx")

print("Loading Piper voice:", MODEL_PATH)
voice = PiperVoice.load(MODEL_PATH)
print("Piper voice loaded.")

class TTSHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            if self.path != "/tts":
                self.send_response(404)
                self.end_headers()
                return

            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            data = json.loads(body)

            text = data.get("text", "").strip()
            output_path = data.get("output_path", "").strip()

            output_path = output_path.replace("/", "\\")
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            print("TTS text:", text)
            print("Output:", output_path)

            with wave.open(output_path, "wb") as wav_file:
                voice.synthesize_wav(text, wav_file)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True}).encode("utf-8"))

        except Exception as e:
            print("PIPER SERVER ERROR:")
            traceback.print_exc()

            self.send_response(500)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(str(e).encode("utf-8"))

if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 5005), TTSHandler)
    print("Piper server running at http://127.0.0.1:5005")
    server.serve_forever()