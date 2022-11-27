import socket
import hashlib
import threading
import rsa

ID = ""

def recv_msg(user):
    if user.startswith('<'):
        while True:
            data = ClientMultiSocket.recv(2048).decode('utf-8').split('|')
            if data[0] == '--':
                return
            else:
                print("-> " + user + "-" + data[0] + ": " + data[1])
    else:
        while True:
            data = ClientMultiSocket.recv(2048)
            if data == str.encode('--'):
                return
            else:
                decrypted = rsa.decrypt(data, privateKey).decode('ascii')        
                print("-> " + user + ": " + decrypted)

def send_msg(public):
    if public == rsa.key.PublicKey(0, 0):
        while True:
            data = input()
            ClientMultiSocket.sendall(str.encode(data))
            if data == "--":
                return
    else:
        while True:
            data = input()
            if data == "--":
                ClientMultiSocket.sendall(str.encode(data))
                return
            else:
                encrypted = rsa.encrypt(data.encode('ascii'), public)
                ClientMultiSocket.sendall(encrypted)

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
(publicKey, privateKey) = (0, 0)

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
            with open(ID+".txt", 'r') as f:
                lines = f.read().split("\n")
                pub = lines[0].split("-")
                pri = lines[1].split("-")
                publicKey = rsa.key.PublicKey(int(pub[0]), int(pub[1]))
                privateKey = rsa.key.PrivateKey(int(pri[0]), int(pri[1]), int(pri[2]), int(pri[3]), int(pri[4]))
                f.close()
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
            (publicKey, privateKey) = rsa.newkeys(1024)
            with open(ID+".txt", 'w') as f:
                f.write(str(publicKey.n) + "-" + str(publicKey.e) + "\n")
                f.write(str(privateKey.n) + "-" + str(privateKey.e) + "-" + str(privateKey.d) + "-" + str(privateKey.p) + "-" + str(privateKey.q))
                f.close()
            ClientMultiSocket.send(str.encode(str(publicKey.n)+"-"+str(publicKey.e)))
            break

server_port = int(ClientMultiSocket.recv(2048).decode('utf-8'))
ClientMultiSocket.close()

ClientMultiSocket = socket.socket()
print('Waiting for connection response')
try:
    ClientMultiSocket.connect((host, server_port))
except socket.error as e:
    print(str(e))

ClientMultiSocket.send(str.encode(ID))

while True:
    end = 0
    public_string = ""
    user = ""
    while True:
        print(ClientMultiSocket.recv(2048).decode('utf-8'))
        while True:
            sender = ClientMultiSocket.recv(2048).decode('utf-8')
            if sender == ":)":
                break
            if sender.split(' ')[1].startswith('<'):
                message = ClientMultiSocket.recv(2048).decode('utf-8')
            elif sender.split(' ')[1].startswith('#'):
                message = ClientMultiSocket.recv(2048).decode('utf-8')
            else:
                message = rsa.decrypt(ClientMultiSocket.recv(2048), privateKey).decode('ascii')
            print(sender+message)

        Input = input('Who do you want to talk to?: ')
        user = Input
        ClientMultiSocket.send(str.encode(Input))
        if Input.startswith('#CG'):
            user = Input.split('-')[1]
        if Input == "no one":
            end = 1
            break
        msg = ClientMultiSocket.recv(2048).decode('utf-8')
        print(msg)
        if msg == "********************":
            if not (Input.startswith('#CG') or Input.startswith('<')):
                public_string = ClientMultiSocket.recv(2048).decode('utf-8')
            print(ClientMultiSocket.recv(2048).decode('utf-8'))
            while True:
                sender = ClientMultiSocket.recv(2048).decode('utf-8')
                if sender == ":)":
                    break
                if Input.startswith('<'):
                    message = ClientMultiSocket.recv(2048).decode('utf-8')
                else:
                    message = ClientMultiSocket.recv(2048)
                    message = rsa.decrypt(message, privateKey).decode('ascii')
                print(sender+message)
            break
        else:
            continue
    if end == 1:
        break
    if public_string == "":
        public = rsa.key.PublicKey(0, 0)
    else:
        n_e = public_string.split("-")
        public = rsa.key.PublicKey(int(n_e[0]), int(n_e[1]))
    t = threading.Thread(target=recv_msg, args=[user])
    t.start()
    send_msg(public)
    t.join()
        
ClientMultiSocket.close()
