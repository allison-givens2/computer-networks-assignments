import socket
import argparse
import sys
from packet import Packet, TYPE_DATA

class HelloClient:
    def __init__(self, host="127.0.0.1", port=-1, bufsize=4096):
        self.host = host
        self.port = port
        self.bufsize = bufsize

    def send_and_receive(self, message: str) -> str:
        if self.port == -1:
            print("Error: Port not set. Use --port <number>.")
            sys.exit(1)

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host, self.port))

        # Create packet
        packet = Packet.create(message, TYPE_DATA)
        s.sendall(packet)

        # Receive reply
        data = s.recv(self.bufsize)
        s.close()

        pkt_type, msg = Packet.parse(data)
        return msg

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hello Client")
    parser.add_argument("--port", type=int, default=-1)
    parser.add_argument("--message", type=str, required=True)
    args = parser.parse_args()

    client = HelloClient(port=args.port)
    print("Received:", client.send_and_receive(args.message))
