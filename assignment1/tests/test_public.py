import sys, os
import unittest
import subprocess
import time
import socket

# add assignment folder to sys.path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from client import HelloClient

HOST = "127.0.0.1"
PORT = 5078   # Example: 5000 + last two digits of TECH ID
BUF  = 4096

class TestHelloSockets(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = subprocess.Popen(
            ["python3", "server.py", "--port", str(PORT)]
        )
        time.sleep(0.5)

    @classmethod
    def tearDownClass(cls):
        cls.server.terminate()
        cls.server.wait()

    # 1. Server is running
    def test_server_running(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, PORT))
        s.close()

    # 2. Client can connect
    def test_client_can_connect(self):
        c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        c.connect((HOST, PORT))
        c.close()

    # 3. Client can send
    def test_client_can_send(self):
        c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        c.connect((HOST, PORT))
        c.sendall(b"Ping")
        c.close()

    # 4. Server echoes
    def test_server_echoes(self):
        cli = HelloClient(HOST, PORT, BUF)
        reply = cli.send_and_receive("World")
        self.assertEqual(reply, "Hello, World")

    # 5. Oversized message should trigger AssertionError on server
    def test_long_message_error(self):
        long_msg = "A" * (BUF + 1)  # too long
        cli = HelloClient(HOST, PORT, BUF)
        reply = cli.send_and_receive(long_msg)
        self.assertEqual(reply, "ERROR: message too long")

