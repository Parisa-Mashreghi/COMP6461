import socket
import argparse
import threading
import os
import libhttp
from colorama import Fore

def create_parser():
    parser = argparse.ArgumentParser(prog="httpfs",
                                     add_help=True,
                                     description="httpfs is a simple file server.")
    parser.add_argument("-v", "--verbose", help="Prints debugging messages.", action="store_true", default=False, required=False)
    parser.add_argument("-p", "--port", help="Specifies the port number that the server will listen and serve at. Default is 8080.", type=int, default=8080, required=False)
    parser.add_argument("-d", "--dir", help="Specifies the directory that the server will use to read/write requested files. Default is the current directory when launching the application.", type=str, default="./", required=False)

    args = parser.parse_args()
    return args

def create_http_file_server(host, port, dir, log):
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_sock.bind((host, port))
        server_sock.listen(20)
        if log:
            print('File server is listening to port = ', port)
        while True:
            client_sock, client_host = server_sock.accept()
            threading.Thread(target=incoming_connection, args=(client_sock, client_host, dir, log)).start()
    finally:
        server_sock.close()

def incoming_connection(sock, host, dir, log):
    if log:
        print(Fore.GREEN + f'\nNew client {host} is connected.' + Fore.RESET)
    try:
        data = sock.recv(4096)
        request = libhttp.parse_request(data, log)
        if request.is_valid():
            response = request.do(dir)
            sock.send(response.to_bytearray())
    finally:
        if log:
            print(Fore.RED + f'Client {host} was closed.' + Fore.RESET)
        sock.close()

    
# -------------------------------------------------------
# Main function
# -------------------------------------------------------
def main():
    # Create a command line parser
    args = create_parser()

    # Create a server socket for the file server

    server_sock = create_http_file_server('', args.port, args.dir, args.verbose)

if __name__ == "__main__":
    main()
