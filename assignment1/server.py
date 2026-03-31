import socket
import argparse
import sys

class HelloServer:
    def __init__(self, host="", port=-1, bufsize=1024):
        self.host = host
        self.port = port
        self.bufsize = bufsize
        self.sock = None

    def start(self):
        if self.port == -1:
            print("Error: Port not set. Use --port <number>.")
            sys.exit(1)


        # Create socket, bind to (host, port), listen
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))

        # Accept client connections in a loop
        self.sock.listen()
        print(f"Server listening on {self.host or '0.0.0.0'}:{self.port}")

        # Receive message (up to bufsize+1 bytes)
        while True:
            conn, addr = self.sock.accept()
            with conn:
                print(f"Connected by {addr}")
                message = conn.recv(self.bufsize + 1)
        # Handle empty message
            #   - If empty: send back b"Empty message"
                if  not message or message.decode() == "<empty>" :
                    send_back = b"Empty message"
                    conn.sendall(send_back)

        # Handle Oversized message
            #   - If message too long: send back b"ERROR: message too long"
                elif len(message) > self.bufsize:
                    send_back = b"ERROR: message too long"
                    conn.sendall(send_back)

        #   - Otherwise: send back the message client sent. Add Hello at the beginning.
            # - Return b"Hello, Message"
            # - if client sent "I am client", you will return b"Hello, I am client"
            # - make sure you encode as UTF-8, something like "message.encode("utf-8")"
                else:
                    send_back = b"Hello, " + message
                    conn.sendall(send_back)


    def stop(self):
        if self.sock:
            self.sock.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hello Server")
    parser.add_argument("--port", type=int, default=-1, help="Port number to bind the server on")
    args = parser.parse_args()

    server = HelloServer(port=args.port)
    server.start()