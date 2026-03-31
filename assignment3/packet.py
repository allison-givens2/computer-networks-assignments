import struct
import zlib

MAGIC = 0xC0DE
VER   = 0x01
TYPE_DATA = 0
TYPE_ACK  = 1
TYPE_ERR  = 2

# Base header: MAGIC(2) VER(1) TYPE(1) SEQ(4) LEN(2) CHK(4)
_HDR_FMT = "!HBBIHI"
_HDR_SIZE = struct.calcsize(_HDR_FMT)
MAX_PAYLOAD = 1000

# Last packet adds file checksum (FCHK, 4 bytes)
_HDR_LAST_FMT = "!HBBIHI I"
_HDR_LAST_SIZE = struct.calcsize(_HDR_LAST_FMT)

class Packet:
    @staticmethod
    def checksum(data: bytes) -> int:
        """
        Compute CRC32 checksum (truncate to 32 bits).
        """
        # TODO: implement checksum using zlib.crc32
        return zlib.crc32(data) & 0xFFFFFFFF

    @staticmethod
    def create(seq: int, data: bytes, pkt_type: int = TYPE_DATA, file_checksum: int = None) -> bytes:
        """
        Build a packet with header + payload.
        - Normal packets: include CHK
        - Last packet: include CHK + FCHK
        """
        # TODO: 1) Ensure payload ≤ MAX_PAYLOAD
        if len(data) > MAX_PAYLOAD:
            raise ValueError("Payload too large")
        length = len(data)
        payload = data

        # TODO: 2) Pack header with CHK=0 (and include FCHK if final packet)
        if file_checksum is not None:
            header = struct.pack(_HDR_LAST_FMT, MAGIC, VER, pkt_type, seq, length, 0, file_checksum)
        else:
            header = struct.pack(_HDR_FMT, MAGIC, VER, pkt_type, seq, length, 0)

        # TODO: 3) Compute checksum over header+payload
        CHK = Packet.checksum(header + payload)

        # TODO: 4) Repack header with correct CHK
        if file_checksum is not None:
            header = struct.pack(_HDR_LAST_FMT, MAGIC, VER, pkt_type, seq, length, CHK, file_checksum)
        else:
            header = struct.pack(_HDR_FMT, MAGIC, VER, pkt_type, seq, length, CHK)

        # TODO: 5) Return header+payload
        return header + payload


    @staticmethod
    def parse(packet: bytes):
        """
        Parse packet into (pkt_type, seq, data, file_checksum or None).
        Validate MAGIC, VER, LEN, CHK.
        """
        # TODO: 1) Ensure header is long enough
        if len(packet) < _HDR_SIZE:
            raise ValueError("Packet too short to contain base header")

        # TODO: 2) Unpack base header, validate MAGIC & VER
        magic, ver, pkt_type, seq, length, chk = struct.unpack(_HDR_FMT, packet[:_HDR_SIZE])
        file_checksum = None

        if magic != MAGIC or ver != VER:
            raise ValueError("Invalid MAGIC or VER")

        # TODO: 5) Handle last packet with FCHK
        expected_total = _HDR_SIZE + length
        if len(packet) == _HDR_LAST_SIZE + length:
            magic, ver, pkt_type, seq, length, chk, file_checksum = struct.unpack(_HDR_LAST_FMT, packet[:_HDR_LAST_SIZE])
            header_size = _HDR_LAST_SIZE
        else:
            header_size = _HDR_SIZE
        
        # TODO: 3) Check payload length matches LEN
        payload = packet[header_size:header_size + length]
        if len(payload) != length:
            raise ValueError("Payload length mismatch")

        # TODO: 4) Recompute checksum, compare with CHK
        if file_checksum is not None:
            header = struct.pack(_HDR_LAST_FMT, magic, ver, pkt_type, seq, length, 0, file_checksum)
        else:
            header = struct.pack(_HDR_FMT, magic, ver, pkt_type, seq, length, 0)
        if Packet.checksum(header + payload) != chk:
            raise ValueError("Checksum mismatch")

        return pkt_type, seq, payload, file_checksum

