# server.py (AIMD Skeleton)
import socket
import argparse
import random
import zlib
import time
from packet import Packet, TYPE_ACK, TYPE_DATA

class UDPServer:
    def __init__(self, host="127.0.0.1", port=6000, outfile="received.bin", loss_rate=0.9):
        self.host = host
        self.port = port
        self.outfile = outfile
        self.loss_rate = loss_rate
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.host, self.port))
        self.buffer = {}
        self.final_seq = None
        self.final_checksum = None
        self.file_written = False

        print(f"Server running on {self.host}:{self.port}, ACK drop rate={self.loss_rate}")

    def start(self):
        print("Server listening for packets (skeleton)...")
        while True:
            packet, addr = self.sock.recvfrom(2048)
            try:
                pkt_type, seq, data, fchk = Packet.parse(packet)

                if pkt_type == TYPE_DATA:
                    # TODO: Store data chunk
                    if seq not in self.buffer:
                        self.buffer[seq] = data
                    #raise NotImplementedError("Data buffering not implemented")

                    # TODO: Randomly drop ACKs (simulate packet loss)
                    if random.random() < self.loss_rate:
                        continue
                    #raise NotImplementedError("ACK drop simulation not implemented")

                    # TODO: Send ACK back to client
                    ack = Packet.create(seq, b"", TYPE_ACK)
                    time.sleep(self.ack_delay if hasattr(self, 'ack_delay') else 0)
                    self.sock.sendto(ack, addr)
                    #raise NotImplementedError("ACK sending not implemented")

                    # TODO: On final packet (FCHK present),
                    # verify full file checksum and write to disk
                    if fchk is not None:
                        self.final_seq = seq + 1        
                        self.final_checksum = fchk
                    if self.final_seq is not None and len(self.buffer) == self.final_seq and not self.file_written:
                        ordered_chunks = [self.buffer[i] for i in range(self.final_seq)]
                        full_file = b"".join(ordered_chunks)
                        chk_calc = zlib.crc32(full_file) & 0xFFFFFFFF
                        if chk_calc == self.final_checksum:
                            with open(self.outfile, "wb") as f:
                                f.write(full_file)
                                self.file_written = True
                        else:
                            self.buffer.clear()
                    #raise NotImplementedError("Final checksum verification not implemented")

            except Exception as e:
                print("Error parsing packet or unimplemented logic:", e)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UDP File Server with AIMD (Skeleton)")
    parser.add_argument("--host", type=str, default="127.0.0.1")
    parser.add_argument("--port", type=int, default=6000)
    parser.add_argument("--outfile", type=str, default="received.bin")
    parser.add_argument("--loss", type=float, default=0.1, help="ACK drop probability (0-1)")
    args = parser.parse_args()

    server = UDPServer(host=args.host, port=args.port, outfile=args.outfile, loss_rate=args.loss)
    server.start()

