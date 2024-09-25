from dotenv import load_dotenv
from os.path import join, dirname
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, HTTPServer

dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)

from aidbox.base import API

from HL7v2.ADT import A01, A02, A03, A04, A08
from HL7v2.ORU import R01
from HL7v2.ORM import O01
from HL7v2.VXU import V04

import json
import requests
import time

def worker(interval):
    timestamp = datetime.now().replace(microsecond=0).isoformat()
    print(f"[{timestamp}]: mapping HL7v2 service has started.")
    while True:
        try:
            response = API.request(endpoint="/Hl7v2Message?.status=error&_count=1")
            
            if response.status_code == 200:
                data = response.json()
                process_data(data)
                API.request(endpoint="/Hl7v2Message?.status=error&_count=1", method="PATCH", json={"status": "processed"})
        
        except Exception as e:
            if f"{e}" != "list index out of range": 
                print(f"Error: {e}")
        
        time.sleep(interval)

def process_data(data):
    message = data['entry'][0]

    if message is None: return

    if message['resource']['type'] == 'ADT':
        if message['resource']['event'] == 'A01':
            A01.run(message['resource']["parsed"]["parsed"])

        if message['resource']['event'] == 'A08':
            A08.run(message['resource']["parsed"]["parsed"])

worker(10)


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

        if self.path == "/HL7v2/ADT_A04":
            request_wrapper(self, A04.run)

        if self.path == "/HL7v2/ADT_A08":
            request_wrapper(self, A08.run)

        if self.path == "/HL7v2/ORU_R01":
            request_wrapper(self, R01.run)

        if self.path == "/HL7v2/ORM_O01":
            request_wrapper(self, O01.run)

        if self.path == "/HL7v2/VXU_V04":
            request_wrapper(self, V04.run)


if __name__ == "__main__":
    server_address = ("localhost", 8000)
    server = HTTPServer(server_address, HL7v2)
    print("Serving HTTP on port 8000...")
    server.serve_forever()
