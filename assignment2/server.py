import socket
import argparse
import sys
from packet import Packet, TYPE_DATA, TYPE_ERR

class HelloServer:
    def __init__(self, host="127.0.0.1", port=-1, bufsize=4096):
        self.host = host
        self.port = port
        self.bufsize = bufsize
        self.sock = None

    def start(self):
        if self.port == -1:
            print("Error: Port not set. Use --port <number>.")
            sys.exit(1)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.listen(1)
        print(f"Server listening on {self.host}:{self.port}")

        while True:
            conn, addr = self.sock.accept()
            with conn:
                data = conn.recv(self.bufsize)
                if not data:
                    continue

                try:
                    pkt_type, msg = Packet.parse(data)
                    if pkt_type == TYPE_DATA:
                        reply = Packet.create(f"Hello, {msg}")
                    else:
                        reply = Packet.create("Unexpected packet", TYPE_ERR)
                except Exception as e:
                    reply = Packet.create(f"ERROR: {str(e)}", TYPE_ERR)

                conn.sendall(reply)

    def stop(self):
        if self.sock:
            self.sock.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hello Server")
    parser.add_argument("--port", type=int, default=-1)
    args = parser.parse_args()
    HelloServer(port=args.port).start()
