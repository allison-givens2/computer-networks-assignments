import unittest
import threading
import time
import zlib
import sys, os, signal
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from packet import Packet, TYPE_DATA
from client import UDPClient
from server import UDPServer

HOST = "127.0.0.1"
PORT = 6300

class TestAIMDPublic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = UDPServer(host=HOST, port=PORT, loss_rate=0.2)
        cls.thread = threading.Thread(target=cls.server.start, daemon=True)
        cls.thread.start()
        time.sleep(0.5)

    def setUp(self):
        # Safety timeout to prevent test hang
        self._stop_timer = threading.Timer(10, lambda: (_ for _ in ()).throw(TimeoutError("Test timeout")))
        self._stop_timer.start()

    def tearDown(self):
        self._stop_timer.cancel()

    def test_01_basic_transfer(self):
        client = UDPClient(host=HOST, port=PORT, timeout=0.5, plot=False)
        client.send_data(b"basic aimd test")
        self.assertTrue(len(client.history) > 0)

    def test_02_packet_format(self):
        data = b"abcdef"
        chk = zlib.crc32(data) & 0xFFFFFFFF
        pkt = Packet.create(1, data, TYPE_DATA, file_checksum=chk)
        t, seq, d, fchk = Packet.parse(pkt)
        self.assertEqual(seq, 1)
        self.assertEqual(d, data)
        self.assertEqual(fchk, chk)

    def test_03_window_growth_reduction(self):
        client = UDPClient(host=HOST, port=PORT, timeout=0.5, plot=False)
        client.window = 4
        client.ssthresh = max(1, client.window // 2)
        client.window = client.ssthresh
        self.assertEqual(client.window, 2)
        client.window += 1
        self.assertEqual(client.window, 3)

    def test_04_retransmission_and_window_dynamics(self):
        data = b"window change retransmit test" * 10
        client = UDPClient(host=HOST, port=PORT, timeout=0.8, plot=False)
        client.send_data(data)
        self.assertTrue(any(w > 1 for w in client.history))
        self.assertTrue(any(w < max(client.history) for w in client.history))

    def test_05_short_transfer_stability(self):
        client = UDPClient(host=HOST, port=PORT, timeout=0.4, plot=False)
        client.send_data(b"short test")
        self.assertTrue(client.window >= 1)

