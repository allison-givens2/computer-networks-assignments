# Computer Networks Assignments

This is a compilation of the assignments completed for the Computer Networks Course (Fall 2025).

## Assignment 1 – Simple Client-Server Socket Program
**Objective:**  Introduction to network programming using Python sockets.
**Summary:** Implemented a basic client-server application using Python’s socket library. The client sends a simple message to the server, and the server responds, demonstrating the fundamentals of TCP connections, binding, listening, and sending/receiving data.

## Assignment 2 – Create Packets
**Objective:**  Building a tiny, class-based client/server that talks over TCP using a custom binary packet.
**Summary:** Developed a TCP client-server system that exchanges structured binary packets. Each packet includes headers and payload, allowing for flexible message types. This assignment reinforced understanding of data serialization, packet framing, and handling multiple message types over a network connection.

## Assignment 3 – Large Data Transfer
**Objective:**  Building a class-based client/server that exchanges large data (~1 MB) over UDP using a custom binary packet.
**Summary:** Extended the client-server architecture to reliably send and receive large files over UDP. Implemented chunking of data into packets, sequence numbering, and reassembly on the receiving end, demonstrating UDP’s connectionless behavior and the need for application-level reliability.

## Assignment 4 – Retransmission
**Objective:**  Implement a reliable file transfer protocol on top of UDP.
**Summary:** Built a custom protocol that ensures reliable delivery over UDP by detecting lost packets and performing retransmissions. Implemented acknowledgment messages, timeouts, and basic error checking to guarantee complete file transfer despite UDP’s unreliable nature.

## Assignment 5 – AIMD Reliable File Transfer over UDP
**Objective:**  Implement reliable file transfer over UDP using AIMD (Additive Increase / Multiplicative Decrease) congestion control.
**Summary:** Enhanced the UDP file transfer protocol with congestion control using the AIMD algorithm. The system dynamically adjusts the sending rate based on network feedback, reducing packet loss and improving overall throughput while maintaining reliability.

## Assignment 6 – UDP Overlay (Project Part 1)
**Objective:**  Establishing the networking layer for distributed learning, trust computation, and model exchange in later assignments
**Summary:** Designed and implemented a peer-to-peer overlay network using UDP sockets. Each node can join the overlay, discover peers, and maintain connectivity. This lays the foundation for secure model exchange and distributed computation in subsequent assignments.

## Assignment 7 – Exchange Updates (Project Part 2)
**Objective:**  Extending PeerNode overlay to support large binary transfers.
**Summary:** Expanded the UDP overlay to handle the exchange of large binary updates between peers. Implemented reliable multi-part transfers, sequencing, and peer management to ensure updates propagate correctly across the distributed network.

## Assignment 8 – LLM Prompts (Project Part 3)
**Objective:**  Implementing the networking mechanisms that enable model deltas to be transmitted, received, verified, and merged
**Summary:** Built the final layer of the peer-to-peer network to support secure and verified transmission of model deltas. Implemented integrity checks, merging mechanisms, and efficient transmission protocols to enable collaborative model updates among peers.
