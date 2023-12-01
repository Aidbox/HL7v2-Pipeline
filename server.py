from dotenv import load_dotenv
from os.path import join, dirname
from http.server import SimpleHTTPRequestHandler, HTTPServer

dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)

from aidbox.base import API

from HL7v2.ADT import A01, A02, A03, A04, A08
from HL7v2.ORU import R01
from HL7v2.ORM import O01

import json
import requests


def convert_message(message):
    response = API.request(
        endpoint="/hl7in/ADT", method="POST", json={"message": message}
    )
    response.raise_for_status()
    return response.json()


def request_wrapper(self, action):
    content_length = int(self.headers["Content-Length"])
    post_data = self.rfile.read(content_length).decode("utf-8")

    try:
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

        parsed_data = convert_message(post_data)
        print(parsed_data.keys())
        action(parsed_data["parsed"]["parsed"])

        response = json.dumps({"message": "DONE"})
        self.wfile.write(response.encode("utf-8"))

    except requests.exceptions.RequestException as e:
        print(e)
        if e.response is not None:
            print(e.response.json())

    except json.JSONDecodeError:
        self.send_response(400)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bad Request: Invalid JSON")


class HL7v2(SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/HL7v2/ADT_A01":
            request_wrapper(self, A01.run)

        if self.path == "/HL7v2/ADT_A02":
            request_wrapper(self, A02.run)

        if self.path == "/HL7v2/ADT_A03":
            request_wrapper(self, A03.run)

        if self.path == "/HL7v2/ADT_A03":
            request_wrapper(self, A04.run)

        if self.path == "/HL7v2/ADT_A03":
            request_wrapper(self, A04.run)

        if self.path == "/HL7v2/ORU_R01":
            request_wrapper(self, R01.run)

        if self.path == "/HL7v2/ORM_O01":
            request_wrapper(self, O01.run)


if __name__ == "__main__":
    server_address = ("localhost", 8000)
    server = HTTPServer(server_address, HL7v2)
    print("Serving HTTP on port 8000...")
    server.serve_forever()
