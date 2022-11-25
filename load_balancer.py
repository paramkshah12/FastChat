import socket
import os
import threading
import psycopg2
import time
from _thread import *

ServerSideSocket = socket.socket()
host = '127.0.0.1'
port = 2004
server_sockets = []
duration = 0

ports = [4000, 4001, 4002, 4003, 4004]

conn = psycopg2.connect(
   database="postgres", user='param', password='password', host='127.0.0.1', port= '5432'
)
conn.autocommit = True
cursor = conn.cursor()
cursor.execute('''DROP DATABASE IF EXISTS store''')
cursor.execute('''CREATE database store''')
print("Database created successfully........")
conn.close()

conn = psycopg2.connect(database="store", user="param")
cur = conn.cursor()
cur.execute('''DROP TABLE IF EXISTS KEY''')
cur.execute('''CREATE TABLE KEY
      (RECIPIENT_ID TEXT NOT NULL,
      N TEXT NOT NULL);''')
cur.execute('''DROP TABLE IF EXISTS MSGS''')
cur.execute('''CREATE TABLE MSGS
      (RECIPIENT_ID TEXT NOT NULL,
      MSG BYTEA NOT NULL,
      SENDER_ID TEXT NOT NULL,
      DURATION REAL);''')
cur.execute('''DROP TABLE IF EXISTS FROMTO''')
cur.execute('''CREATE TABLE FROMTO
      (SENDER_ID TEXT NOT NULL,
      RECIPIENT_ID TEXT NOT NULL);''')
cur.execute('''DROP TABLE IF EXISTS CLIENTS''')
cur.execute('''CREATE TABLE CLIENTS
        (SERVER_NUMBER INT,
        ID TEXT);''')
cur.execute('''DROP TABLE IF EXISTS COUNT''')
cur.execute('''CREATE TABLE CC
        (SERVER_NUMBER INT,
        COUNT INT);''')
cur.execute('''DROP TABLE IF EXISTS GROUPS''')
cur.execute('''CREATE TABLE GROUPS
        (NAME TEXT,
        MEMBERS TEXT)''')

for i in range(5):
    cur.execute('''INSERT INTO CC (SERVER_NUMBER, COUNT) \
        VALUES (%s, 0)''',
        (i, ))
conn.commit()
print("Tables created successfully")

try:
    ServerSideSocket.bind((host, port))
except socket.error as e:
    print(str(e))
print('Socket is listening..')
ServerSideSocket.listen()

def multi_threaded_server(connection):
    while True:
        f_t = connection.recv(2048).decode('utf-8').split("|")
        message = connection.recv(2048)
        f = f_t[0]
        t = f_t[1]
        if not t.startswith('<'):
            is_online = 0
            server_number = 0
            cur.execute('''SELECT * FROM CLIENTS WHERE ID=%s''',
                (t, ))
            rows = cur.fetchall()
            if len(rows) != 0:
                is_online = 1
                server_number = rows[0][0]
            if is_online == 1:
                cur.execute('''SELECT * FROM FROMTO WHERE SENDER_ID=%s''',
                    (t, ))
                if message == str.encode("--"):
                    time.sleep(0.1)
                    connection.send(str.encode(t))
                    time.sleep(0.3)
                    connection.send(message)

                elif cur.fetchone()[1] == f:
                    time.sleep(0.1)
                    server_sockets[server_number].send(str.encode(t))
                    time.sleep(0.1)
                    server_sockets[server_number].send(message)
                else:
                    cur.execute('''INSERT INTO MSGS (RECIPIENT_ID,MSG,SENDER_ID,DURATION) \
                        VALUES (%s, %s, %s, %s);
                        ''',
                        (t, psycopg2.Binary(message), f, duration))
                    conn.commit()
            else:
                cur.execute('''INSERT INTO MSGS (RECIPIENT_ID,MSG,SENDER_ID,DURATION) \
                    VALUES (%s, %s, %s, %s);
                    ''',
                    (t, psycopg2.Binary(message), f, duration))
                conn.commit()
        else:
            cur.execute('''SELECT * FROM GROUPS WHERE NAME=%s''',
                (t, ))
            members = cur.fetchone()[1].split('-')
            for member in members:
                if member == f:
                    continue
                is_online = 0
                server_number = 0
                cur.execute('''SELECT * FROM CLIENTS WHERE ID=%s''',
                    (member, ))
                rows = cur.fetchall()
                if len(rows) != 0:
                    is_online = 1
                    server_number = rows[0][0]
                if is_online == 1:
                    cur.execute('''SELECT * FROM FROMTO WHERE SENDER_ID=%s''',
                        (member, ))
                    if message == str.encode("--"):
                        time.sleep(0.1)
                        connection.send(str.encode(member))
                        time.sleep(0.3)
                        connection.send(message)

                    elif cur.fetchone()[1] == t:
                        time.sleep(0.1)
                        server_sockets[server_number].send(str.encode(t+"-"+f+"-"+member))
                        time.sleep(0.1)
                        server_sockets[server_number].send(message)
                    else:
                        cur.execute('''INSERT INTO MSGS (RECIPIENT_ID,MSG,SENDER_ID,DURATION) \
                            VALUES (%s, %s, %s, %s);
                            ''',
                            (member, message, t+"-"+f, duration))
                        conn.commit()
                else:
                    cur.execute('''INSERT INTO MSGS (RECIPIENT_ID,MSG,SENDER_ID,DURATION) \
                        VALUES (%s, %s, %s, %s);
                        ''',
                        (member, message, t+"-"+f, duration))
                    conn.commit()

def multi_threaded_client(connection):
    ch = int(connection.recv(2048).decode('utf-8'))
    ID = ""

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
                with open("credentials.txt", 'a') as f:
                    f.write("\n" + ID + " " + Hash)
                f.close()
                connection.send(str.encode("You have registered successfully!"))
                public = connection.recv(2048).decode('utf-8')
                cur.execute('''INSERT INTO KEY (RECIPIENT_ID, N) \
                VALUES (%s, %s);
                ''',
                (ID, public))
                conn.commit()
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
                        connection.send(str.encode("Logged in Successfully!"))
                        match = 1
                        f.close()
                        break
                if match == 1:
                    break
                else:
                    connection.send(str.encode("Login failed!"))
                    continue

    cur.execute('''SELECT * FROM CC''')
    rows = cur.fetchall()
    client_count = [0, 0, 0, 0, 0]
    for row in rows:
        client_count[row[0]] = row[1]
    minimum = min(client_count)
    server_number = 0
    while client_count[server_number] != minimum:
        server_number += 1
    connection.send(str.encode(str(ports[server_number])))
    cur.execute('''UPDATE CC
            SET COUNT=%s
            WHERE SERVER_NUMBER=%s''',
            (client_count[server_number]+1, server_number))
    cur.execute('''INSERT INTO CLIENTS (SERVER_NUMBER, ID) \
        VALUES (%s, %s);
        ''',
        (server_number, ID))
    conn.commit()
    return

for i in range(5):
    Server, address = ServerSideSocket.accept()
    print('Connected to: ' + address[0] + ':' + str(address[1]))
    server_sockets.append(Server)
    start_new_thread(multi_threaded_server, (Server, ))

while True:
    Client, address = ServerSideSocket.accept()
    print('Connected to: ' + address[0] + ':' + str(address[1]))
    t = threading.Thread(target=multi_threaded_client, args=[Client])
    t.start()
    t.join()
