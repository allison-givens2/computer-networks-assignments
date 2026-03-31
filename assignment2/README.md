[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/swYE62ao)
## Objective

Build a tiny, class-based client/server that talks over TCP using a **custom binary packet**.
Students will implement **packet creation and decoding** with:


# Packet Header Format

The header is **9 bytes total**, followed by the payload.

```

| Field    | Size (bytes) | Description                        |
| -------- | ------------ | ---------------------------------- |
| MAGIC    | 2            | Fixed constant `0xC0DE`            |
| VER      | 1            | Protocol version (currently 0x01)  |
| TYPE     | 1            | Packet type (DATA=0, ACK=1, ERR=2) |
| RESERVED | 1            | Reserved for future use (set 0)    |
| LEN      | 2            | Payload length in bytes (≤4096)    |
| CHK      | 2            | 16-bit checksum of header+payload  |

```

---

### Visual Layout

```

0      1      2      3      4      5      6      7      8
+------+------+------+------+------+------+------+------+
\|   MAGIC (0xC0DE)   | VER  | TYPE | RSVD |      LEN     |
+------+------+------+------+------+------+------+------+
\|          CHK (16 bits)          |
+------+------+------+------+------+
\|              PAYLOAD (LEN bytes)                ...
+--------------------------------------------------------+

```

- **MAGIC** helps detect invalid packets.  
- **VER** allows future protocol updates.  
- **TYPE** lets you distinguish DATA, ACK, and ERR messages.  
- **LEN** is the byte length of the payload.  
- **CHK** is a 16-bit checksum over the header (with CHK=0) and payload.  
-----


* A fixed **header**: `MAGIC (2B) | VER (1B) | TYPE (1B) | RESERVED (1B) | LEN (2B) | CHK (2B)` using big-endian (`"!HBBBHH"`).
* **Payload length** in the header.
* **Checksum** computed over **(header with CHK=0) + payload** (CRC32 truncated to 16 bits is fine).

Most of the work is in `packet.py` (skeleton provided). `client.py` and `server.py` are intentionally simple so they “just work” once the packet layer is correct.

---

## Steps

### 1) Implement the Packet layer (students)

Open `packet.py` and complete:

* `checksum(data: bytes) -> int`
* `create(msg: str, pkt_type: int) -> bytes`
* `parse(packet: bytes) -> tuple[int, str]`

Protocol constants you’ll use:

```python
MAGIC = 0xC0DE
VER   = 0x01
TYPE_DATA = 0
TYPE_ACK  = 1
TYPE_ERR  = 2
_HDR_FMT  = "!HBBBHH"
MAX_PAYLOAD = 4096
```

Guidelines:

* Encode payload as UTF-8.
* Set `LEN` to payload byte length.
* Compute checksum over the header assembled with `CHK=0` concatenated with the payload. Then re-pack the header with the real checksum.
* On `parse`, validate: MAGIC, VER, LEN vs actual payload size, checksum.

> Keep it simple and readable; this is a starter exercise.

---

### 2) Run the server

```bash
python3 server.py --port 5078
```

You should see:

```
Server listening on 127.0.0.1:5078
```

### 3) Run the client

In another terminal:

```bash
python3 client.py --port 5078 --message "Alice"
```

Expected console output (once your packet layer is correct):

```
Received: Hello, Alice
```

> Tip: If you get `ModuleNotFoundError: No module named 'packet'` while running tests, add the project root to `sys.path` at the top of test files:
>
> ```python
> import sys, os
> sys.path.append(os.path.dirname(os.path.dirname(__file__)))
> ```

---

## Expected Outcome

* `Packet.create` produces a byte sequence with a correct header (right MAGIC/VER/TYPE/LEN/CHK) followed by payload.
* `Packet.parse` returns `(pkt_type, message)` and raises `ValueError` for malformed inputs.
* The server replies with a `TYPE_DATA` packet containing `Hello, <name>` when receiving a valid `TYPE_DATA` packet.
* The client prints the decoded reply string.

---

## Grading Rubric (10 points total)

Each test is worth one point.

## 5 Public Tests

These are visible and run locally as `tests/test_public.py`:

1. **Packet roundtrip**: `create` then `parse` returns the original message.
2. **Header length**: LEN matches payload size.
3. **Max payload**: 4096-byte payload passes.
4. **Communication works**: client↔server roundtrip returns a non-empty reply.
5. **Correct message**: reply contains `Hello, Alice`.

Run:

```bash
python3 -m unittest tests/test_public.py -v
# or
pytest -q tests/test_public.py
```

---

## 5 Private Test Hints

Hidden tests in grading (do NOT assume their exact names), but you should pass them if you follow the spec:

* **MAGIC** must be exactly `0xC0DE`.
* **VER** must be exactly `0x01`.
* **Checksum tampering** is detected (flip a payload byte ⇒ `ValueError`).
* **Oversized payload** (>4096 bytes) is rejected.
* **Checksum validity**: well-formed packets parse successfully.

Focus areas to avoid surprises:

* Use network byte order (`!` in struct format).
* Set `CHK=0` when computing the checksum, then pack the real checksum.
* Compare LEN with actual payload bytes (not character count—UTF-8 can matter).
* Raise `ValueError` with a helpful message on any validation failure.

---

## Submission

**What to submit**

* `packet.py` (your implementation)
* `client.py`, `server.py` (unchanged or minimally adjusted, but must work)

**How to submit**

* Push to your repository in GitHub classroom.


**Environment**

* Python 3.9+
* Standard library only (`struct`, `zlib`, `socket`, `argparse`, `unittest`). No third-party packages.

**Academic Integrity**

* Write your own code. Discuss concepts, but don’t share implementations.
* You may reuse your own starter/skeleton; do not copy from others.

---

Happy hacking! If anything fails, print the raw bytes of your header to sanity-check field positions and values — it solves 90% of issues.

