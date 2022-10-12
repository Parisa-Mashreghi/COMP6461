# from ast import arg
import socket
import argparse
# import sys
from urllib.parse import urlparse
import libhttp

# Usage: httpc.py (get|post|help) [-h "Key: Value"] [-d inline-data] [-f file] URL
# Ex.1: python3 httpc.py post -h "Content-Type: application/json" -d '{"Assignment": 1}' 'http://httpbin.org/post'
# Ex1.1 python3 httpc.py post -v -h "Content-Type: application/json" -f "data.json" 'http://httpbin.org/post'
# Ex.2: python3 httpc.py get 'http://httpbin.org/get?course=networking&assignment=1'
# Ex.3: python3 httpc.py get -v -o out.txt 'http://httpbin.org/status/301'

def create_parser():
    parser = argparse.ArgumentParser(prog="httpc",
                                     add_help=False,
                                     description="httpc is a curl-like application but supports HTTP protocol only.")
    subparsers = parser.add_subparsers(description="command", help="Commands to run")

    # A subparser for GET command
    parser_get = subparsers.add_parser(name="get",
                                       add_help=False,
                                       description="GET http method")
    parser_get.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true", default=False, required=False)
    parser_get.add_argument("-h", "--headers", nargs='*', help="Header", type=str, default="")
    parser_get.add_argument("-o", "--out", help="Output", type=str, default="")
    parser_get.add_argument("URL", help="HTTP url")
    parser_get.set_defaults(command="get")

    # A subparser for POST command
    parser_post = subparsers.add_parser(name="post",
                                        add_help=False,
                                        description="POST http method")
    parser_post.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true", default=False, required=False)
    parser_post.add_argument("-h", "--headers", nargs='*', help="Header", type=str, default="")
    parser_post.add_argument("-o", "--out", help="Output", type=str, default="")
    parser_post.add_argument("URL", help="HTTP url")
    group_arg = parser_post.add_mutually_exclusive_group(required=False)
    group_arg.add_argument("-d", "--data", help="The inline data for POST method", type=str, default="")
    group_arg.add_argument("-f", "--file", help="The file path for POST method", metavar="path", type=str, default="")
    parser_post.set_defaults(command="post")

    # A subparser for help command
    parser_help = subparsers.add_parser(name="help",
                                        add_help=False,
                                        description="Helps how to use http commands")
    parser_help.add_argument("method", nargs='?', help="HTTP url")
    parser_help.set_defaults(command="help")

    # Parse input arguments entered in CLI
    args = parser.parse_args()
    return args


def show_help_general():
    print("""
httpc is a curl-like application but supports HTTP protocol only.
Usage:
    httpc command [arguments]
The commands are:
    get     executes a HTTP GET request and prints the response.
    post    executes a HTTP POST request and prints the response.
    help    prints this screen.

Use "httpc help [command]" for more information about a command.
    """)


def show_help_get():
    print("""
usage: httpc get [-v] [-h key:value] URL

Get executes a HTTP GET request for a given URL. 

    -v Prints the detail of the response such as protocol, status, and headers. 
    -h key:value Associates headers to HTTP Request with the format 'key:value'.
    """)


def show_help_post():
    print("""
usage: httpc post [-v] [-h key:value] [-d inline-data] [-f file] URL 

Post executes a HTTP POST request for a given URL with inline data or from file. 

    -v Prints the detail of the response such as protocol, status, and headers. 
    -h key:value Associates headers to HTTP Request with the format 'key:value'. 
    -d string Associates an inline data to the body HTTP POST request. 
    -f file Associates the content of a file to the body HTTP POST request. 

Either [-d] or [-f] can be used but not both.
    """)


def create_http_request(args):
    # Check method to initialize variables
    method = libhttp.Method.UNKNOWN
    if args.command == "get":
        method = libhttp.Method.GET
    elif args.command == "post":
        method = libhttp.Method.POST
    else:
        print("Invalid command!\n")
        exit()

    # Create HTTP request
    req = libhttp.HttpRequest(method, args.URL)

    # Add headers
    if "headers" in args:
        headers = dict([match.split(':', 1) for match in args.headers])
        for key in headers:
            req.add_header(key, headers[key])

    # Append inline data or file only for POST method
    if "data" in args:
        if args.data.strip() != "":
            req.add_header("Content-Type", "application/json")
            req.set_data_inline(args.data)
    if "file" in args:
        if args.file.strip() != "":
            req.set_data_file(args.file)
    
    return req


def send_http_request(req):
    # Open TCP socket and send the HTTP request
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ba = req.to_bytearray()
    print("********** Request: **********")
    print(ba.decode("utf-8"))
    try:
        sock.connect((req.host, 80))
        sock.sendall(ba)
        response = sock.recv(4096)
        return response
    finally:
        sock.close()
    return bytearray()


def write_response(filename, response, append):
    mode = "a" if append else "w"
    with open(filename, mode) as f:
        f.write(response.decode("utf-8"))

# -------------------------------------------------------
# Main function
# -------------------------------------------------------
def main():
    # Create a command line parser
    args = create_parser()

    # Check which command is called
    if args.command == "help":
        if "method" in args:
            if args.method == "get":
                show_help_get()
            elif args.method == "post":
                show_help_post()
            else:
                show_help_general()
    else:
        redirection = True
        count = 0
        req = create_http_request(args)
        while redirection == True:
            response = send_http_request(req)
            if "out" in args:
                if args.out.strip() != "":
                    write_response(args.out, response, count!=0) 
    
            # Check verbose option
            print("********** Response: **********")
            response_parts = response.decode("utf-8").split("\r\n\r\n")
            if "verbose" in args:
                if args.verbose == True:
                    print(response_parts[-2] + "\n")
            print(response_parts[-1] + "\n")

            count += 1
            redirection = req.check_redirection(response)


if __name__ == "__main__":
    main()
