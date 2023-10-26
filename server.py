from dotenv import load_dotenv
from os.path import join, dirname
from http.server import SimpleHTTPRequestHandler, HTTPServer

dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)

from aidbox.base import API
import ADT_A08
import json
import requests


def convert_message(message):
    response = API.request(
        endpoint="/hl7in/ADT", json={"message": message}, method="POST"
    )
    response.raise_for_status()
    return response.json()


class HL7v2(SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/HL7v2/ADT_AO8":
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length).decode("utf-8")

            try:
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                parsed_data = convert_message(post_data)
                ADT_A08.run(parsed_data["parsed"]["parsed"]["patient_group"])

                response = json.dumps({"message": "DONE"})
                self.wfile.write(response.encode("utf-8"))

            except requests.exceptions.RequestException as e:
                if e.response is not None:
                    print(e.response.json())

            except json.JSONDecodeError:
                self.send_response(400)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(b"Bad Request: Invalid JSON")


if __name__ == "__main__":
    server_address = ("localhost", 8000)
    server = HTTPServer(server_address, HL7v2)
    print("Serving HTTP on port 8000...")
    server.serve_forever()
