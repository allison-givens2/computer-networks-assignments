import unittest
import threading
import time
import socket
import zlib
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from packet import Packet, TYPE_DATA, TYPE_ACK
from client import UDPClient
from server import UDPServer

HOST = "127.0.0.1"
PORT = 6200

class TestPublic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = UDPServer(host=HOST, port=PORT)
        cls.thread = threading.Thread(target=cls.server.start, daemon=True)
        cls.thread.start()
        time.sleep(0.5)

    # 1. Can talk to each other
    def test_can_talk(self):
        client = UDPClient(host=HOST, port=PORT)
        client.send_data(b"hello world")

    # 2. Can parse headers
    def test_parse_headers(self):
        pkt = Packet.create(0, b"abc", TYPE_DATA)
        t, seq, data, fchk = Packet.parse(pkt)
        self.assertEqual(seq, 0)
        self.assertEqual(data, b"abc")
        self.assertIsNone(fchk)

    # 3. Sequence numbers
    def test_sequence_numbers(self):
        pkt1 = Packet.create(0, b"x", TYPE_DATA)
        pkt2 = Packet.create(1, b"y", TYPE_DATA)
        _, seq1, _, _ = Packet.parse(pkt1)
        _, seq2, _, _ = Packet.parse(pkt2)
        self.assertEqual(seq1, 0)
        self.assertEqual(seq2, 1)

    # 4. Header checksum detects corruption
    def test_checksum_validation(self):
        pkt = bytearray(Packet.create(0, b"abc", TYPE_DATA))
        pkt[-1] ^= 0xFF
        with self.assertRaises(ValueError):
            Packet.parse(bytes(pkt))

    # 5. File checksum present in last packet
    def test_file_checksum_in_last(self):
        data = b"abcdef"
        fullchk = zlib.crc32(data) & 0xFFFFFFFF
        pkt = Packet.create(0, data, TYPE_DATA, file_checksum=fullchk)
        _, seq, parsed, fchk = Packet.parse(pkt)
        self.assertEqual(parsed, data)
        self.assertEqual(fchk, fullchk)

if __name__ == "__main__":
    unittest.main()

