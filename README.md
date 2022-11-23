# FastChat | SSL Project
This is a simple chatting platform built using the socket library in python.
## What we've done:
- So far, we're using a single server to handle all of the client-message requests. Handling multiple clients was achieved using the _thread library.
- There's a log-in/sign-up system that uses the hashlib library in order to hash the passwords for storage and verification. The credentials are stored in a file named 'credentials.txt'.
- When a client is texting another client, it creates a second thread with the server so that it can send and receive messages simultaneously. This was achieved using the threading library.
- When clients comes online, they're first shown any new messages that they had received while they were offline. Then they're asked who they want to talk to and can switch between clients as and when they please. Between every switch, they're again showed any new messages received by other clients while they were busy talking to a particular one. This was achieved by storing and fetching messages in a database appropriately using the psycopg2 library.
- Hence, if client1 chooses to talk to client2 and sends some messages to it, they're either directly sent to client2 only if client2 is online as well as talking back to client1; or they're stored in the data-base and shown to client2 at an appropriate time. 
## How to run:
- Open a terminal and run `brew services start postgresql && psql messages` after installing the required software. 
- Open a terminal and run `python3 server.py`
- Open another termninal and run `python3 multiple-client.py`. This will connect the client to the server and display the log-in/sign-up system.
- Enter correct credentials and you'll be shown all the unread messages or "No new messages!".
- Choose a client you want to talk to when asked "Who do you want to talk to?: "; you must know their ID (username) for this. If you type "no one", the program will end and you'll go offline.
- If you're done talking to a particular client, enter "--". You'll exit the chat room and new messages or "No new messages!" will be displayed again. You'll be asked "Who do you want to talk to?: " again.
- You can open a new terminal and run `python3 multiple-client.py` anytime in order to connect a new client to the server.
## What is yet to be done:
- We're yet to implement multiple servers to handle requests and hence, load balancing.
- We've planned out the end-to-end encryption for messages but it is yet to be programmed.
- Still left to build the notion of groups and the process to send images.
- The code is not well modularised and documented.
## Contributors:
Cheshta Damor - 21005040\
Shah Param Kauhsik - 210050144\
We've worked on almost all the parts of the code together. 
