import socket
import os
from _thread import *

ServerSideSocket = socket.socket()
host = '127.0.0.1'
port = 2004
online = {}

try:
    ServerSideSocket.bind((host, port))
except socket.error as e:
    print(str(e))
print('Socket is listening..')
ServerSideSocket.listen()

def multi_threaded_client(connection):

    ch = int(connection.recv(2048).decode('utf-8'))

    if ch == 1:
        while True:
            match = 0
            ID = connection.recv(2048).decode('utf-8')
            Hash = connection.recv(2048).decode('utf-8')
            with open("credentials.txt", 'r') as f:
                for line in f.read().split("\n"):
                    stored_id, stored_pwd = line.split(" ")
                    if ID == stored_id:
                        connection.send(str.encode("This ID already exists!"))
                        match = 1
                        f.close()
                        break
            if match == 1:
                continue
            else:
                online[ID] = connection
                with open("credentials.txt", 'a') as f:
                    f.write("\n" + ID + " " + Hash)
                f.close()
                connection.send(str.encode("You have registered successfully!"))
                break

    elif ch == 2:
         while True:
            match = 0
            ID = connection.recv(2048).decode('utf-8')
            Hash = connection.recv(2048).decode('utf-8')
            with open("credentials.txt", 'r') as f:
                for line in f.read().split("\n"):
                    stored_id, stored_pwd = line.split(" ")
                    if ID == stored_id and Hash == stored_pwd:
                        online[ID] = connection
                        connection.send(str.encode("Logged in Successfully!"))
                        match = 1
                        f.close()
                        break
                if match == 1:
                    break
                else:
                    connection.send(str.encode("Login failed!"))
                    continue 

    while True:
        to_user = connection.recv(2048).decode('utf-8')
        match = 0
        with open("credentials.txt", 'r') as f:
            for line in f.read().split("\n"):
                stored_id, stored_pwd = line.split(" ")
                if to_user == stored_id:
                    match = 1
                    f.close()
                    break
        if match == 1:
            connection.send(str.encode("********************"))
            break
        else:
            connection.send(str.encode("This user does not exist!"))
            continue

    if to_user in online.keys():
        while True:
            online[to_user].sendall(connection.recv(2048))
    else:
        pass


while True:
    Client, address = ServerSideSocket.accept()
    print('Connected to: ' + address[0] + ':' + str(address[1]))

    start_new_thread(multi_threaded_client, (Client, ))

ServerSideSocket.close()
