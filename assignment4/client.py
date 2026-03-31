import socket
import argparse
import zlib
import time
from packet import Packet, TYPE_DATA, TYPE_ACK

class UDPClient:
    def __init__(self, host="127.0.0.1", port=6000, retries=5, timeout=1.0):
        self.host = host
        self.port = port
        self.retries = retries
        self.timeout = timeout
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setblocking(False)

    def send_data(self, data: bytes):
        # Compute file checksum for final packet
        file_checksum = zlib.crc32(data) & 0xFFFFFFFF
        seq = 0

        for i in range(0, len(data), 1000):
            chunk = data[i:i+1000]

            # TODO: create packet
            # Regular packet
            pkt = Packet.create(seq, chunk, TYPE_DATA)
            #raise NotImplementedError("Regular packet creation not implemented")

            # TODO: retransmission loop with packet-level timeout
            ack_received = False
            for attempt in range(self.retries):
                self.sock.sendto(pkt, (self.host, self.port))
                start = time.time()
                while time.time() - start < self.timeout:
                    try:
                        ack, addr = self.sock.recvfrom(2048)
                        try:
                            pkt_type, ack_seq, _, _ = Packet.parse(ack)
                            if pkt_type == TYPE_ACK and ack_seq == seq:
                                ack_received = True
                                break
                        except ValueError:
                            continue
                    except BlockingIOError:
                        continue
                if ack_received:
                    break
            else:
                raise RuntimeError(f"Failed to send packet {seq}")

            seq += 1

        final_pkt = Packet.create(seq, b"", TYPE_DATA, file_checksum)

        ack_received = False
        for attempt in range(self.retries):
            print(f"Sending final packet {seq}, attempt {attempt + 1}")
            self.sock.sendto(final_pkt, (self.host, self.port))
            start = time.time()
            while time.time() - start < self.timeout:
                try:
                    ack, addr = self.sock.recvfrom(2048)
                    try:
                        pkt_type, ack_seq, _, _ = Packet.parse(ack)
                        if pkt_type == TYPE_ACK and ack_seq == seq:
                            ack_received = True
                            break
                    except ValueError:
                        continue
                except BlockingIOError:
                    continue
            if ack_received:
                break
        else:
            raise RuntimeError(f"Failed to send packet {seq}")

        print("Transfer complete (skeleton — retransmissions not yet implemented).")
        self.sock.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UDP File Client with Retransmissions (Skeleton)")
    parser.add_argument("--host", type=str, default="127.0.0.1")
    parser.add_argument("--port", type=int, default=6000)
    parser.add_argument("--file", type=str, required=True)
    args = parser.parse_args()

    with open(args.file, "rb") as f:
        data = f.read()

    client = UDPClient(host=args.host, port=args.port)
    client.send_data(data)

