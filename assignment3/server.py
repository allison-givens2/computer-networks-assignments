import socket
import zlib
import argparse
from packet import Packet, TYPE_ACK, TYPE_DATA

class UDPServer:
    def __init__(self, host="127.0.0.1", port=6000, outfile="received.bin"):
        self.host = host
        self.port = port
        self.outfile = outfile
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.host, self.port))
        self.buffer = {}

    def start(self):
        print(f"Server listening on {self.host}:{self.port}")
        while True:
            packet, addr = self.sock.recvfrom(2048)
            try:
                pkt_type, seq, data, fchk = Packet.parse(packet)
                if pkt_type == TYPE_DATA:
                    # Store chunk
                    self.buffer[seq] = data

                    # Send ACK back
                    ack = Packet.create(seq, b"", TYPE_ACK)
                    self.sock.sendto(ack, addr)

                    # If final packet received, validate and write file
                    if fchk is not None:
	                # TODO: Reassemble full data from buffer
                        # Reassemble full data from buffer
                        full_data = b''.join(self.buffer[i] for i in sorted(self.buffer))
                        calc = zlib.crc32(full_data) & 0xFFFFFFFF
                        if calc == fchk:
                            print(f"File received correctly. Writing to {self.outfile}")
                            with open(self.outfile, "wb") as f:
                                f.write(full_data)
                        else:
                            print("File checksum mismatch!")
                        # Reset for next transfer
                        self.buffer.clear()
            except Exception as e:
                print("Error parsing packet:", e)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UDP File Server")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind")
    parser.add_argument("--port", type=int, default=6000, help="Port to bind")
    parser.add_argument("--outfile", type=str, default="received.bin", help="File to save received data")
    args = parser.parse_args()

    server = UDPServer(host=args.host, port=args.port, outfile=args.outfile)
    server.start()
