import socket
import argparse
import random
import zlib
from packet import Packet, TYPE_ACK, TYPE_DATA
import time

class UDPServer:
    def __init__(self, host="127.0.0.1", port=6000, outfile="received.bin", loss_rate=1):
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


    def start(self):
        print(f"Server listening on {self.host}:{self.port}")
        while True:
            try:
                packet, addr = self.sock.recvfrom(2048)
                pkt_type, seq, data, fchk = Packet.parse(packet)
                if pkt_type == TYPE_DATA:
                    # TODO: simulate loss
                    if random.random() < self.loss_rate:
                        continue

                    # TODO: buffer packet data
                    if fchk is not None:
                        self.final_seq = seq
                        self.final_checksum = fchk
                    if data:
                        if seq not in self.buffer:
                            self.buffer[seq] = data
    
                    # TODO: send ACK
                    ack = Packet.create(seq, b"", TYPE_ACK)
                    time.sleep(self.ack_delay if hasattr(self, 'ack_delay') else 0)
                    self.sock.sendto(ack, addr)


                    # TODO: final checksum check and file write
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

            except Exception as e:
                print(f"Error parsing packet: {e}")
                try:
                    seq = int.from_bytes(packet[4:8], byteorder='big')
                except:
                    seq = 0  
                ack = Packet.create(seq, b"", TYPE_ACK) 
                self.sock.sendto(ack, addr)
        self.sock.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UDP File Server with Loss Simulation (Skeleton)")
    parser.add_argument("--host", type=str, default="127.0.0.1")
    parser.add_argument("--port", type=int, default=6000)
    parser.add_argument("--outfile", type=str, default="received.bin")
    parser.add_argument("--loss", type=float, default=1, help="Packet loss rate (0-1)")
    args = parser.parse_args()

    server = UDPServer(host=args.host, port=args.port, outfile=args.outfile, loss_rate=args.loss)
    server.start()

