import struct
import zlib

MAGIC = 0xC0DE
VER   = 0x01
TYPE_DATA = 0
TYPE_ACK  = 1
TYPE_ERR  = 2

_HDR_FMT = "!HBBIHI"
_HDR_SIZE = struct.calcsize(_HDR_FMT)
MAX_PAYLOAD = 1000

_HDR_LAST_FMT = "!HBBIHI I"
_HDR_LAST_SIZE = struct.calcsize(_HDR_LAST_FMT)

class Packet:
    @staticmethod
    def checksum(data: bytes) -> int:
        return zlib.crc32(data) & 0xFFFFFFFF

    @staticmethod
    def create(seq: int, data: bytes, pkt_type: int = TYPE_DATA, file_checksum: int = None) -> bytes:
        length = len(data)
        if length > MAX_PAYLOAD:
            raise ValueError("Payload too large")

        if file_checksum is None:
            header = struct.pack(_HDR_FMT, MAGIC, VER, pkt_type, seq, length, 0)
            chk = Packet.checksum(header + data)
            header = struct.pack(_HDR_FMT, MAGIC, VER, pkt_type, seq, length, chk)
            return header + data
        else:
            header = struct.pack(_HDR_LAST_FMT, MAGIC, VER, pkt_type, seq, length, 0, file_checksum)
            chk = Packet.checksum(header + data)
            header = struct.pack(_HDR_LAST_FMT, MAGIC, VER, pkt_type, seq, length, chk, file_checksum)
            return header + data

    @staticmethod
    def parse(packet: bytes):
        if len(packet) < _HDR_SIZE:
            raise ValueError("Incomplete header")

        base_header = packet[:_HDR_SIZE]
        magic, ver, pkt_type, seq, length, chk = struct.unpack(_HDR_FMT, base_header)
        if magic != MAGIC or ver != VER:
            raise ValueError("Bad header")

        if len(packet) == _HDR_SIZE + length:
            data = packet[_HDR_SIZE:]
            header_chk = struct.pack(_HDR_FMT, magic, ver, pkt_type, seq, length, 0)
            calc = Packet.checksum(header_chk + data)
            if calc != chk:
                raise ValueError("Checksum mismatch")
            return pkt_type, seq, data, None

        elif len(packet) == _HDR_LAST_SIZE + length:
            header = packet[:_HDR_LAST_SIZE]
            magic, ver, pkt_type, seq, length, chk, fchk = struct.unpack(_HDR_LAST_FMT, header)
            data = packet[_HDR_LAST_SIZE:]
            header_chk = struct.pack(_HDR_LAST_FMT, magic, ver, pkt_type, seq, length, 0, fchk)
            calc = Packet.checksum(header_chk + data)
            if calc != chk:
                raise ValueError("Checksum mismatch")
            return pkt_type, seq, data, fchk
        else:
            raise ValueError("Length mismatch")

