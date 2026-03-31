import unittest
import threading
import time
import zlib
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from packet import Packet, TYPE_DATA
from client import UDPClient
from server import UDPServer

HOST = "127.0.0.1"
PORT = 6300

class TestPublic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = UDPServer(host=HOST, port=PORT, loss_rate=0.3)
        cls.thread = threading.Thread(target=cls.server.start, daemon=True)
        cls.thread.start()
        time.sleep(0.5)

    def test_can_talk(self):
        client = UDPClient(host=HOST, port=PORT)
        client.send_data(b"hello world")

    def test_parse_headers(self):
        pkt = Packet.create(0, b"abc", TYPE_DATA)
        t, seq, data, fchk = Packet.parse(pkt)
        self.assertEqual(seq, 0)
        self.assertEqual(data, b"abc")

    def test_sequence(self):
        pkt = Packet.create(1, b"xyz", TYPE_DATA)
        _, seq, _, _ = Packet.parse(pkt)
        self.assertEqual(seq, 1)

    def test_retransmission(self):
        client = UDPClient(host=HOST, port=PORT, retries=5)
        try:
            client.send_data(b"test retransmission")
        except RuntimeError as e:
            self.assertIn("Failed to send packet", str(e))

    def test_final_checksum(self):
        data = b"abcdef"
        fullchk = zlib.crc32(data) & 0xFFFFFFFF
        pkt = Packet.create(0, data, TYPE_DATA, file_checksum=fullchk)
        _, _, d, fchk = Packet.parse(pkt)
        self.assertEqual(fchk, fullchk)

    def test_nonblocking_socket(self):
        """Client must not rely solely on socket.settimeout()."""
        client = UDPClient(host=HOST, port=PORT, retries=3)
        client.sock.setblocking(False)
        try:
            client.send_data(b"nonblocking test")
        except RuntimeError as e:
            self.assertIn("Failed to send packet", str(e))

