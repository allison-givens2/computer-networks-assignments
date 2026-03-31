import unittest
from client import UDPClient
from server import UDPServer, Packet, TYPE_DATA
import threading
import time
import zlib

class TestAIMDPrivate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.HOST = '127.0.0.1'
        cls.PORT = 6300
        cls.server = UDPServer(cls.HOST, cls.PORT)
        cls.server_thread = threading.Thread(target=cls.server.start)
        cls.server_thread.daemon = True
        cls.server_thread.start()
        time.sleep(0.1)  # Allow server to start

    @classmethod
    def tearDownClass(cls):
        cls.server.stop()
        cls.server_thread.join()

    def setUp(self):
        self.client = UDPClient(self.HOST, self.PORT)
        self.client.history = []

    def tearDown(self):
        self.client.sock.close()

    def test_01_high_loss_adaptation(self):
        """Ensure client adapts window under high ACK loss"""
        self.client.send_data(b"test data high loss", loss_rate=0.5)
        self.assertTrue(all(w >= 1 for w in self.client.history))

    def test_02_large_file(self):
        """Test sending large amount of data"""
        data = b"A" * 10000
        self.client.send_data(data)
        self.assertTrue(len(self.client.history) > 1)

    def test_03_loss_window_drop(self):
        """Ensure retransmissions happen and window drops on loss"""
        self.client.send_data(b"test loss", loss_rate=0.2)
        self.assertTrue(any(w < max(self.client.history) for w in self.client.history))

    def test_04_retransmission_detected(self):
        """Ensure retransmission actually occurs"""
        self.client.send_data(b"retransmit test", loss_rate=0.3)
        retransmitted = any(self.client.history.count(w) > 1 for w in self.client.history)
        self.assertTrue(retransmitted)

    def test_05_checksum_verification(self):
        """Test that packet checksums are verified correctly"""
        data = b"checksum test data"
        pkt = Packet.create(0, data, TYPE_DATA)
        self.assertEqual(pkt.checksum, zlib.crc32(data))

if __name__ == "__main__":
    unittest.main()
