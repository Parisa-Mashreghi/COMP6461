from operator import methodcaller
import socket
import sys
import enum
from urllib.parse import urlparse


class Method(enum.Enum):
    UNKNOWN = 0
    GET = 1
    POST = 2


class HttpRequest:
    def __init__(self, method, url):
        url_parts = urlparse(url)
        host = "www." + url_parts.netloc
        path = url_parts.path
        if url_parts.query != "":
            path += "?" + url_parts.query
        self.host = host
        self.path = path
        self.method = method
        self.headers = {}
        self.data = ""

    def set_method(self, method):
        self.method = method

    def set_host(self, host):
        self.host = host

    def set_path(self, path):
        self.path = path

    def add_header(self, key, val):
        self.headers[key] = val

    def set_data_inline(self, data):
        self.data = data

    def set_data_file(self, filename):
        with open(filename, "r") as f:
            self.data = f.read()

    def check_redirection(self, response):
        hdrs = response.decode("utf-8").split("\r\n\r\n")[-2].split("\r\n")     # Extract the headers of the response
        check = int(hdrs[0].split(" ")[1])        # Extract the HTTP status code from the first header
        if 299 < check < 400:                     # A status code between 300 and 399 is recognized redirection response
            location = ""
            for hdr in hdrs:
                hdr = hdr.lower()
                if "location:" in hdr:
                    location = hdr.split("location: ")[1].strip()
            if location != "":
                self.path = location
                return True
        return False

    def to_bytearray(self):
        cr = "\r\n"
        # Add method
        s1 = ""
        if self.method == Method.GET:
            s1 = "GET"
        elif self.method == Method.POST:
            s1 = "POST"
        else:
            s1 = "GET"

        # Add path
        s2 = self.path

        # Add HTTP version
        s3 = "HTTP/1.0"

        # Add headers
        self.add_header("Host", self.host)
        if len(self.data.strip()) != 0:
            self.add_header("Content-Length", len(self.data))
        s4 = ""
        for key in self.headers:
            s4 += f"{cr}{key}: {self.headers[key]}"

        # Add data    
        s5 = cr + cr + self.data + cr

        # Construct the request
        req = f"{s1} {s2} {s3} {s4} {s5}"
        return bytearray(req, "ascii")
