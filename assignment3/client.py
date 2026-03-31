import socket
import argparse
import zlib
from packet import Packet, TYPE_DATA

class UDPClient:
    def __init__(self, host="127.0.0.1", port=6000):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(1)

    def send_data(self, data: bytes):
        file_checksum = zlib.crc32(data) & 0xFFFFFFFF
        seq = 0
        for i in range(0, len(data), 1000):
            chunk = data[i:i+1000]

            # TODO: If this is the last packet, include file_checksum
            # pkt = Packet.create(......)
            # else: normal packet
            # pkt = Packet.create(......)
            if i + 1000 >= len(data):
                pkt = Packet.create(seq, chunk, TYPE_DATA, file_checksum)
            else:
                pkt = Packet.create(seq, chunk, TYPE_DATA)


            self.sock.sendto(pkt, (self.host, self.port))

            try:
                ack, _ = self.sock.recvfrom(2048)
                ack_type, ack_seq, _, _ = Packet.parse(ack)
                if ack_seq != seq:
                    print(f"Unexpected ACK seq {ack_seq}, expected {seq}")
            except socket.timeout:
                print(f"Timeout waiting for ACK {seq}")

            seq += 1

        # TODO: Print message confirming transfer complete
        # and that the final checksum was sent
        print("Transfer complete (final checksum not yet verified).")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UDP File Client")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Server host")
    parser.add_argument("--port", type=int, default=6000, help="Server port")
    parser.add_argument("--file", type=str, required=True, help="File to send")
    args = parser.parse_args()

    with open(args.file, "rb") as f:
        data = f.read()

    client = UDPClient(host=args.host, port=args.port)
    client.send_data(data)

