import socket
import argparse
import sys

class HelloClient:
    def __init__(self, host="127.0.0.1", port=-1, bufsize=4096): #10.142.205.89 149.149.2.105
        self.host = host
        self.port = port
        self.bufsize = bufsize

    def send_and_receive(self, message: str) -> str:
        if self.port == -1:
            print("Error: Port not set. Use --port <number>.")
            sys.exit(1)

        # Empty message is invalid
        #assert message != "", "Empty message is not allowed"
        #
        if message == "":
            message_send = "<empty>"
        else:
            message_send = message

        # Create a socket and close socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

            # Connect to server
            s.connect((self.host, self.port))

            # Send message
            s.sendall(message_send.encode())

            # Receive reply from server
            data = s.recv(self.bufsize)

            # return reply
            return data.decode()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hello Client")
    parser.add_argument("--port", type=int, default=-1, help="Port number to connect to")
    parser.add_argument("--message", type=str, default="", help="Message to send to server")
    args = parser.parse_args()

    client = HelloClient(port=args.port)
    response = client.send_and_receive(args.message)
    print("Received:", response)

