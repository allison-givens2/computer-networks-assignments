import struct
import zlib

# Protocol constants
MAGIC = 0xC0DE
VER   = 0x01

TYPE_DATA = 0
TYPE_ACK  = 1
TYPE_ERR  = 2

# Header format: magic(2) ver(1) type(1) reserved(1) length(2) checksum(2)
# TODO: Pack it below
_HDR_FMT = "!HBBBHH"
_HDR_SIZE = struct.calcsize(_HDR_FMT)
MAX_PAYLOAD = 4096

class Packet:
    @staticmethod
    def checksum(data: bytes) -> int:
        """Compute a 16-bit checksum. Students can use CRC32 truncated."""
        # TODO: Implement checksum (HINT: zlib.crc32(data) & 0xFFFF)
        return zlib.crc32(data) & 0xFFFF

    @staticmethod
    def create(msg: str, pkt_type: int = TYPE_DATA) -> bytes:
        """Create a packet with header + payload."""
        payload = msg.encode("utf-8")
        length = len(payload)
        if length > MAX_PAYLOAD:
            raise ValueError("Payload too large")

        # TODO: Pack header with checksum=0
        # HINT: header = struct.pack(_HDR_FMT, Other fields)
        header = struct.pack("!HBBBHH", 0xC0DE, 0x01, pkt_type, 0, length, 0)
        packet = header + payload

        # TODO: Calculate checksum over header+payload
        if len(packet) < _HDR_SIZE:
            raise ValueError("Packet too short")

        # TODO: Repack header with real checksum
        chk = Packet.checksum(header + payload)
        header = struct.pack("!HBBBHH", 0xC0DE, 0x01, pkt_type, 0, length, chk)

        # return header + payload
        return header + payload


    @staticmethod
    def parse(packet: bytes) -> tuple[int, str]:
        """Parse a packet, return (type, decoded_message)."""
        if len(packet) < _HDR_SIZE:
            raise ValueError("Incomplete header")

        # TODO: unpack header
        # HINT: magic, ver, pkt_type, reserved, length, checksum = struct.unpack(...)
        magic, ver, pkt_type, rsvd, length, chk = struct.unpack(_HDR_FMT, packet[:_HDR_SIZE])

        # TODO: check magic, version, length
        if magic != MAGIC:
            raise ValueError("Bad MAGIC")
        if ver != VER:
            raise ValueError("Bad VER")
        payload = packet[_HDR_SIZE:]

        # TODO: recompute checksum, compare with header field
        header_wo_chk = struct.pack(_HDR_FMT, magic, ver, pkt_type, rsvd, length, 0)
        calc_chk = Packet.checksum(header_wo_chk + payload)
        if chk != calc_chk:
            raise ValueError("Bad checksum")

        # TODO: decode payload into string and return
        return pkt_type, payload.decode("utf-8")

