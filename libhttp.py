from operator import methodcaller
import socket
import argparse
import sys
import enum


class Method(enum.Enum):
    UNKNOWN = 0
    GET = 1
    POST = 2


class HttpRequest:
    def __init__(self, method, url):
        self.method = method
        self.url = url
        self.headers = {}
        self.data = ""

    def set_method(self, method):
        self.method = method

    def set_url(self, url):
        self.url = url

    def add_header(self, key, val):
        self.headers[key] = val

    def set_data_inline(self, data):
        self.data = data

    def set_data_file(self, filename):
        try:
            f = open(filename, "rb")
            self.data = f.read()
        finally:
            f.close()

    def redirect(self, response):
        resp = response
        head = resp.split("\r\n")
        check = int(head[0].split(" ")[1])
        if 299 < check < 400:
            for headers in head:
                if "Location: " in headers:
                    location = headers.split("Location: ")[1]
            if location:
                return location
            else:
                return None

    def to_string(self):
        cr = "\r\n"
        # Add method
        s1 = ""
        if self.method == Method.GET:
            s1 = "GET"
        elif self.method == Method.POST:
            s1 = "POST"
        else:
            s1 = "GET"

        # Add URI
        s2 = self.url

        # Add HTTP version
        s3 = "HTTP/1.1"

        # Add headers
        if len(self.data.strip()) != 0:
            self.add_header("Content-Length", len(self.data))
        s4 = ""
        for key in self.headers:
            s4 += f"{cr}{key}: {self.headers[key]}"

        # Add data    
        s5 = cr + cr + self.data + cr

        # Construct the request
        req = f"{s1} {s2} {s3} {s4} {s5}"

        print(req)
        return bytearray(req, "ascii")


def run_client(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, port))

        url = "/get?course=networking&assignment=1"
        req = HttpRequest(Method.GET, url)
        req.add_header("Host", host)
        req.add_header("Content-Type", "application/json")
        req.set_data_inline("{ \"Greeting\": \"Hello\" }")
        sock.sendall(req.to_string())
        response = sock.recv(4096, socket.MSG_WAITALL)
        print(response.decode("utf-8"))
    finally:
        sock.close()
