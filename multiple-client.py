import socket
import hashlib
import threading

def recv_msg(user):
    while True:
        data = ClientMultiSocket.recv(2048).decode('utf-8')
        if data == '--':
            return
        else:        
            print("-> " + user + ": " + data)

def send_msg():
    while True:
        data = input()
        ClientMultiSocket.sendall(str.encode(data))
        if data == "--":
            return

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

ch = 0

while True:
    ch = str(input("Enter your choice: "))
    if ch == '1' or ch == '2':
        break
    else:
        print("Choose between 1 or 2 only!")

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
    end = 0
    while True:
        print(ClientMultiSocket.recv(2048).decode('utf-8')) 
        Input = input('Who do you want to talk to?: ')
        ClientMultiSocket.send(str.encode(Input))
        if Input == "no one":
            end = 1
            break
        msg = ClientMultiSocket.recv(2048).decode('utf-8')
        print(msg)
        if msg == "********************":
            print(ClientMultiSocket.recv(2048).decode('utf-8'))
            break
        else:
            continue
    if end == 1:
        break
    t = threading.Thread(target=recv_msg, args=[Input])
    t.start()
    send_msg()
    t.join()
        
ClientMultiSocket.close()
