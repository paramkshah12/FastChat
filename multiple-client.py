import socket
import hashlib

ClientMultiSocket = socket.socket()
host = '127.0.0.1'
port = 2004
print('Waiting for connection response')
try:
    ClientMultiSocket.connect((host, port))
except socket.error as e:
    print(str(e))

print("********** Login System **********")
print("1: Signup")
print("2: Login")
ch = str(input("Enter your choice: "))
ClientMultiSocket.send(str.encode(ch))

if ch == '2':
    while True:
        ID = input("Enter ID: ")
        Pass = input("Enter Password: ")
        enc = Pass.encode()
        hash1 = hashlib.md5(enc).hexdigest()
        ClientMultiSocket.send(str.encode(ID)) 
        ClientMultiSocket.send(str.encode(hash1))
        msg = ClientMultiSocket.recv(2048).decode("utf-8")
        print(msg)
        if msg == "Login failed!":
            continue
        else:
            break

elif ch == '1':
    while True:
        ID = input("Enter ID: ")
        Pass = input("Enter Password: ")
        enc = Pass.encode()
        hash1 = hashlib.md5(enc).hexdigest()
        ClientMultiSocket.send(str.encode(ID)) 
        ClientMultiSocket.send(str.encode(hash1))
        msg = ClientMultiSocket.recv(2048).decode("utf-8")
        print(msg)
        if msg == "This ID already exists!":
            continue
        else:
            break
           
while True:
    Input = input('Who do you want to talk to?: ')
    ClientMultiSocket.send(str.encode(Input))
    res = ClientMultiSocket.recv(1024)
    print(res.decode('utf-8'))
ClientMultiSocket.close()
