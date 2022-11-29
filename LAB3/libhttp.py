from operator import methodcaller
import socket
import sys
import enum
import os
import json
from urllib.parse import urlparse
from colorama import Fore
from lockfile import LockFile


class Method(enum.IntEnum):
    UNKNOWN = 0
    GET = 1
    POST = 2


class StatusCode(enum.IntEnum):
    OK = 200,
    BAD_REQUEST = 400,
    NOT_FOUND = 404


class HttpResponse:
    def __init__(self, status=StatusCode.OK, log=False):
        self.status = status
        self.headers = {}
        self.data = " "
        self.log = False

    def get_status_code(self):
        return self.status

    def set_status_code(self, code):
        self.status = code

    def get_status_string(self):
        str = 'Unknown'
        if self.status == StatusCode.OK:
            str = 'OK'
        elif self.status == StatusCode.BAD_REQUEST:
            str = 'Bad Request'
        elif self.status == StatusCode.NOT_FOUND:
            str = 'Not Found'
        return str

    def add_header(self, key, val):
        self.headers[key] = val

    def set_data_inline(self, data):
        self.data = data

    def set_data_file(self, filename):
        with open(filename, "r") as f:
            self.data = f.read()

    def to_bytearray(self):
        cr = "\r\n"

        # Add HTTP version and status
        s1 = "HTTP/1.0 " + str(int(self.status)) + \
             " " + self.get_status_string()

        # Add headers
        if len(self.data.strip()) != 0:
            self.add_header("Content-Length", len(self.data))
        s2 = ""
        for key in self.headers:
            s2 += f"{cr}{key}: {self.headers[key]}"

        # Add data
        s3 = cr + cr + self.data + cr

        # Construct the request
        resp = f"{s1} {s2} {s3}"
        return bytearray(resp, "ascii")


class HttpRequest:
    def __init__(self, method, url, log=False):
        url_parts = urlparse(url)
        host = "" + url_parts.netloc
        path = url_parts.path
        if url_parts.query != "":
            path += "?" + url_parts.query
        self.host = host
        self.path = path
        self.method = method
        self.headers = {}
        self.data = ""
        valid = False
        if self.method == Method.GET or self.method == Method.POST:
            valid = True
        self.valid = valid
        self.log = log

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

    def is_valid(self):
        return self.valid

    def print_log(self, str, color):
        if self.log:
            print(color + '[Log] ' + str + Fore.RESET)

    def check_redirection(self, response):
        # Extract the headers of the response
        head = response.decode("utf-8").split("\r\n\r\n")[0]
        if head.strip() == "":
            return False
        hdrs = head.split("\r\n")
        # Extract the HTTP status code from the first header
        check = int(hdrs[0].split(" ")[1])
        if 299 < check < 400:  # A status code between 300 and 399 is recognized redirection response
            location = ""
            for hdr in hdrs:
                hdr = hdr.lower()
                if "location:" in hdr:
                    location = hdr.split("location: ")[1].strip()
            if location != "":
                self.path = location
                return True
        return False

    def do(self, dir):
        # Check and correct directories
        if dir.startswith("."):
            dir = dir[1:]
        elif not dir.startswith("/"):
            dir = "/" + dir
        if dir.endswith("/"):
            dir = dir[:-1]
        if self.path == "":
            self.path = "/"
        # Generate the absolute path
        abs_path = os.getcwd() + dir + self.path
        # Create a response
        response = HttpResponse(log=self.log)
        try:
            # Check unauthorized access for security reasons
            if "/.." in abs_path:
                response.set_status_code(StatusCode.BAD_REQUEST)
                response.add_header("Content-Type", "application/json")
                response.set_data_inline("Access denied!")
                self.print_log(f'Access denied -> {abs_path}', Fore.RED)
            # --- GET method ---
            elif self.method == Method.GET:
                # (DIR) Request list of files in the given directory
                if abs_path.endswith("/") and os.path.exists(abs_path):
                    response.set_status_code(StatusCode.OK)
                    response.add_header("Content-Type", "application/json")
                    files = os.listdir(abs_path)
                    response.set_data_inline(json.dumps(files))
                    self.print_log(f'List directory {abs_path}: \n{json.dumps(files)}', Fore.BLUE)
                # (FILE) Request a file
                elif os.path.exists(abs_path):
                    response.set_status_code(StatusCode.OK)
                    response.add_header("Content-Type", "application/json")
                    response.set_data_file(abs_path)
                    self.print_log(f'Request file -> {abs_path}', Fore.BLUE)
                # (NOT FOUND) The path or file is not found
                else:
                    response.set_status_code(StatusCode.NOT_FOUND)
                    response.add_header("Content-Type", "application/json")
                    response.set_data_inline("No such file or directory")
                    self.print_log(f'No such file or directory -> {abs_path}', Fore.YELLOW)
            # --- POST method ---
            elif self.method == Method.POST:
                # Set a sample file name if it was not entered
                if abs_path.endswith("/"):
                    abs_path += 'sample.txt'
                # Extract the base file name
                cdir = os.path.dirname(abs_path)
                # Create the directory if does not exist
                if not os.path.exists(cdir):
                    self.print_log(f'Path {abs_path} did not exist.', Fore.YELLOW)
                    os.makedirs(cdir, exist_ok=True)
                    self.print_log(f'Path {abs_path} was created.', Fore.WHITE)
                # Lock the path
                path_lock = LockFile(abs_path)
                path_lock.acquire()
                # Write the data into the file
                with open(abs_path, 'w') as f:
                    self.print_log(f'The data is successfully written to {abs_path}', Fore.WHITE)
                    f.write(self.data + "\n")
                # Realease the lock
                path_lock.release()
                response.set_status_code(StatusCode.OK)
            # --- UNKNOWN method ---
            else:
                response.set_status_code(StatusCode.BAD_REQUEST)
                response.add_header("Content-Type", "application/json")
                response.set_data_inline("UNKNOWN method")
                self.print_log('UNKNOWN method', Fore.YELLOW)
        # A system error occurred
        except OSError as e:
            response.set_status_code(StatusCode.BAD_REQUEST)
            response.add_header("Content-Type", "application/json")
            response.set_data_inline(e.strerror)
            self.print_log(f'Error -> {e.strerror}', Fore.RED)
        return response

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
        req = f'{s1} {s2} {s3} {s4} {s5}'
        return bytearray(req, "ascii")


def parse_request(data, log):
    (head, body) = data.decode("utf-8").split("\r\n\r\n")
    hdrs = head.split("\r\n")
    line = hdrs.pop(0).split(" ")
    if line[0] == "GET":
        method = Method.GET
    elif line[0] == "POST":
        method = Method.POST
    else:
        method = Method.UNKNOWN
    path = line[1]
    query = ""
    if "?" in path:
        path, query = path.split("?")
    elif "&" in path:
        path, query = path.split("&")

    req = HttpRequest(method, path, log)

    for hdr in hdrs:
        pair = hdr.split(":")
        req.add_header(pair[0], pair[1])

    req.set_data_inline(body)

    return req
