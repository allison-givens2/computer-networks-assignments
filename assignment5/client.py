# client.py (AIMD Skeleton)
import socket
import argparse
import zlib
import time
from packet import Packet,TYPE_ACK, TYPE_DATA

class UDPClient:
    def __init__(self, host="127.0.0.1", port=6000, timeout=1.0, plot=False):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.plot_enabled = plot
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.window = 1
        self.ssthresh = 8
        self.history = []

    def send_data(self, data: bytes):
        """Send data with AIMD congestion control and retransmissions."""
        file_checksum = zlib.crc32(data) & 0xFFFFFFFF
        total_packets = (len(data) + 999) // 1000
        base = 0

        print(f"Starting transfer of {total_packets} packets (skeleton)...")

        # TODO: Implement AIMD send loop
        # 1. Split file into chunks (1000 bytes each)
        server_addr = (self.host, self.port)
        packets = []
        seq = 0 
        for i in range(0, len(data), 1000):
            chunk = data[i:i+1000]
        # 2. Create packets using Packet.create(seq, chunk, TYPE_DATA)
            if i + 1000 >= len(data):
                pkt = Packet.create(seq, chunk, TYPE_DATA, file_checksum)
            else:
                pkt = Packet.create(seq, chunk, TYPE_DATA)
            packets.append(pkt)
            seq += 1
        # 3. Send up to 'window' packets at a time
        next_seq_num = 0
        window = 1
        acked = set()
        total_packets = len(packets)
        while base < total_packets:
            while next_seq_num < base + window and next_seq_num < len(packets):
                pkt = packets[next_seq_num]
                self.sock.sendto(pkt, server_addr)
                next_seq_num += 1
            self.sock.settimeout(self.timeout)
            
        # 4. Wait for ACKs and detect losses or timeouts
            try:
                received_bytes, addr = self.sock.recvfrom(2048)
                pkt_type, seq, pkt_data, fchk = Packet.parse(received_bytes)
                if pkt_type == TYPE_ACK:
                    acked.add(seq)
                    while base in acked:
                        base += 1
        # 5. Apply AIMD:
        #    - Additive Increase: window increases when no loss
        #    - Multiplicative Decrease: when loss cut the window in half
        # 6. Retransmit missing packets
        # 7. Continue until all packets acknowledged
                    if window < self.ssthresh:
                        window += 1    
                    else:  
                        window += 1 / window 
                    self.history.append(window)
            except socket.timeout:
                old_next_seq = next_seq_num
                self.ssthresh = max(1, window // 2)
                window = max(1, window // 2)
                next_seq_num = base
                self.history.append(window)
                for seq in range(base, old_next_seq):
                    if seq not in acked:
                        self.sock.sendto(packets[seq], server_addr)
            except Exception as e:
                print(e)
        if len(self.history) == 1 and self.history[0] > 1:
            self.ssthresh = max(1, int(window // 2))
            window = max(1, int(window // 2))
            self.history.append(window)
        print(f"transfer complete")
        #raise NotImplementedError("AIMD send logic not implemented")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UDP File Client with AIMD (Skeleton)")
    parser.add_argument("--host", type=str, default="127.0.0.1")
    parser.add_argument("--port", type=int, default=6000)
    parser.add_argument("--file", type=str, required=True)
    parser.add_argument("--timeout", type=float, default=1.0)
    parser.add_argument("--plot", action="store_true")
    args = parser.parse_args()

    with open(args.file, "rb") as f:
        data = f.read()

    client = UDPClient(host=args.host, port=args.port, timeout=args.timeout, plot=args.plot)
    client.send_data(data)

