[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/vbBGeh81)
# Assignment 1: Simple Client–Server Socket Program

## Objective
The objective of this assignment is to introduce you to network programming using Python sockets.  
You will implement a simple Hello Server and Hello Client that communicate over TCP.  

This exercise will help you understand how to:
- Create sockets
- Bind and listen on a port
- Accept client connections
- Send and receive messages
- Handle basic error conditions

---

## Steps
1. **Server**
   - Implement `HelloServer.start()`
     - Create a TCP socket
     - Bind it to `(host, port)`
     - Call `listen()`
     - Accept connections in a loop

   - When receiving data:
     - If no data → send back `"Empty message"`
     - If data length > `bufsize` → send back `"ERROR: message too long"`
     - Otherwise → prepend `"Hello, "` and send back

2. **Client**
   - Implement `HelloClient.send_and_receive(message)`
     - Create a TCP socket
     - Connect to the server
     - Send the message
     - Receive the reply
     - Close the socket
     - Return the reply as a string

3. **Command-line arguments**
   - Both client and server must take `--port` argument via `argparse`.
   - Example:
     ```bash
     python server.py --port 5078
     python client.py --port 5078 --message World
     ```
   - Expected output:
     ```
     Received: Hello, World
     ```

---

## Expected Outcome
- Running the server starts a socket listening on the specified port.
- Running the client connects to the server and exchanges messages.
- Program should handle:
  - Normal messages → `"Hello, <msg>"`
  - Empty messages → `"Empty message"`
  - Oversized messages (>4096 bytes) → `"ERROR: message too long"`

---

## Grading Rubric (10 points total)

Each testcase is worth **1 point**. Your score is the number of testcases passed.

### Public tests (5 points) — `tests/test_public.py`
1. **Server running** — `test_server_running`: Server accepts a TCP connection. (1 pt)  
2. **Client connect** — `test_client_can_connect`: Client establishes TCP connection. (1 pt)  
3. **Client send** — `test_client_can_send`: Client sends bytes without error. (1 pt)  
4. **Server echo** — `test_server_echoes`: Response equals `Hello, World`. (1 pt)  
5. **Oversized message** — `test_long_message_error`: Oversized message returns `ERROR: message too long`. (1 pt)  

### Private tests hints (5 points) — `tests/test_private.py`
1. **Echo exact**  (1 pt)  
2. **Empty message** (1 pt)  
3. **Large message (within buffer)**  (1 pt)  
4. **Large message (exceeds buffer)** (1 pt)  
5. **Multiple sequential messages** (1 pt)  

---


### Submission
1. Accept the GitHub Classroom invitation provided by your instructor.  

2. Clone your repository onto your local machine:  
   ```bash
   git clone <your-repo-url>
   cd assignment1-simple-client-server

   ```  
3. Update client.py and server.py with your code 

4. Commit and push your changes:  
   ```bash
   git commit -m "Meaningful comment here"
   git push
   ```  
5. Check GitHub Actions under the repository’s **Actions** tab. Confirm all tests run and pass.  

---
