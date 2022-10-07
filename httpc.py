#from ast import arg
import socket
import argparse
#import sys
from urllib.parse import urlparse
import libhttp

# Usage: httpc.py (get|post|help) [-h "Key: Value"] [-d inline-data] [-f file] URL
# Ex.1: python3 httpc.py post -h "Content-Type: application/json" -d '{"Assignment": 1}' 'http://httpbin.org/post'
# Ex.2: python3 httpc.py get 'http://httpbin.org/get?course=networking&assignment=1'

# -------------------------------------------------------
# Main command line parser
parser = argparse.ArgumentParser(prog="httpc", 
                                 #usage="%(prog)s command",
                                 add_help=False, 
                                 description="httpc is a curl-like application but supports HTTP protocol only.")

subparsers = parser.add_subparsers(description="command", help="Commands to run")

# A subparser for GET command
parser_get = subparsers.add_parser(name="get",
                                   #usage="%(name)s [arguments] URL",
                                   add_help=False, 
                                   description="GET http method")
parser_get.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true", required=False)
parser_get.add_argument("-h", "--header", nargs='*', help="Header", type=str, default="")
parser_get.add_argument("URL", help="HTTP url")
parser_get.set_defaults(command="get")

# A subparser for POST command
parser_post = subparsers.add_parser(name="post", 
                                    #usage="%(name)s [arguments] URL",
                                    add_help=False, 
                                    description="POST http method")
parser_post.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true", required=False)
parser_post.add_argument("-h", "--headers", nargs='*', help="Header", type=str, default="")
parser_post.add_argument("URL", help="HTTP url")
group_arg = parser_post.add_mutually_exclusive_group(required=False)
group_arg.add_argument("-d", "--data", help="The inline data for POST method", type=str, default="")
group_arg.add_argument("-f", "--file", help="The file path for POST method", metavar="path", type=str, default="")
parser_post.set_defaults(command="post")

# A subparser for help command
parser_help = subparsers.add_parser(name="help", 
                                    #usage="%(name)s Method",
                                    add_help=False, 
                                    description="Helps how to use http commands")
parser_help.add_argument("Method", nargs='?', help="HTTP url")
parser_help.set_defaults(command="help")

# Parse input arguments entered in CLI
args = parser.parse_args()

# -------------------------------------------------------
# Check which command is called
if args.command == "help":
    # TODO: Organize help comments for all conditions
    parser_help.print_help()
else:
    # Check method to initialize variables
    method = libhttp.Method.UNKNOWN
    url_parts = urlparse(args.URL)
    host = "www." + url_parts.netloc
    url_path = url_parts.path
    if args.command == "get":
        method = libhttp.Method.GET
        url_path += "?" + url_parts.query
    elif args.command == "post":
        method = libhttp.Method.POST
    else:
        exit()
    
    # Create HTTP request
    req = libhttp.HttpRequest(method=method, url=url_path)

    # Add headers
    req.add_header("Host", host)
    if "headers" in args:
        headers = dict([match.split(':', 1) for match in args.headers])
        for key in headers:
            req.add_header(key, headers[key])

    # Append inline data or file only for POST method
    if "data" in args:
        req.add_header("Content-Type", "application/json")
        req.set_data_inline(args.data)
    elif "file" in args:
        req.set_data_file(args.file)

    # Open TCP socket and send the HTTP request
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, 80))
        sock.sendall(req.to_string())
        response = sock.recv(4096)
        print(response.decode("utf-8"))
        # TODO: Save output if [-o] option is entered
    finally:
        sock.close() 
