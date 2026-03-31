from packet import Packet, TYPE_DATA

print("Running simulated private tests...\n")

# 1️⃣ Well-formed packet works
try:
    pkt = Packet.create("Hello", TYPE_DATA)
    pkt_type, msg = Packet.parse(pkt)
    print("✅ Well-formed packet:", pkt_type, msg)
except Exception as e:
    print("❌ Well-formed packet failed:", e)

# 2️⃣ MAGIC must be 0xC0DE
try:
    bad_header = bytearray(pkt)
    bad_header[0] = 0x00  # corrupt first byte of MAGIC
    Packet.parse(bad_header)
except ValueError as e:
    print("✅ Bad MAGIC detected:", e)

# 3️⃣ VER must be 0x01
try:
    bad_header = bytearray(pkt)
    bad_header[2] = 0x02  # corrupt version
    Packet.parse(bad_header)
except ValueError as e:
    print("✅ Bad VER detected:", e)

# 4️⃣ Checksum tampering
try:
    corrupt_pkt = bytearray(pkt)
    corrupt_pkt[-1] ^= 0xFF  # flip last payload byte
    Packet.parse(corrupt_pkt)
except ValueError as e:
    print("✅ Checksum tampering detected:", e)

# 5️⃣ Oversized payload (>4096)
try:
    Packet.create("A" * 5000, TYPE_DATA)
except ValueError as e:
    print("✅ Oversized payload rejected:", e)

print("\nAll simulated private tests ran.")
