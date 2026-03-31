import unittest
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from packet import Packet, TYPE_DATA

class TestPublic(unittest.TestCase):
    # 6. Magic number must be 0xC0DE
    def test_header_magic(self):
        pkt = Packet.create("x", TYPE_DATA)
        magic = (pkt[0] << 8) | pkt[1]
        self.assertEqual(magic, 0xC0DE)

    # 7. Version must be 0x01
    def test_header_version(self):
        pkt = Packet.create("x", TYPE_DATA)
        self.assertEqual(pkt[2], 0x01)

    # 8. Bad checksum raises error
    def test_bad_checksum(self):
        pkt = bytearray(Packet.create("test", TYPE_DATA))
        pkt[-1] ^= 0xFF
        with self.assertRaises(ValueError):
            Packet.parse(bytes(pkt))

    # 9. Too large payload raises error
    def test_payload_too_large(self):
        with self.assertRaises(ValueError):
            Packet.create("a" * 5000, TYPE_DATA)

    # 10. Header + payload checksum must be valid
    def test_checksum_valid(self):
        pkt = Packet.create("check", TYPE_DATA)
        t, msg = Packet.parse(pkt)
        self.assertEqual(msg, "check")

if __name__ == "__main__":
    unittest.main()

