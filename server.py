import socket
import os
from _thread import *
import psycopg2
import time


ServerSideSocket = socket.socket()
host = '127.0.0.1'
port = 2004
online = {}
from_to = {}
duration = 0

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
print("Table created successfully")

try:
    ServerSideSocket.bind((host, port))
except socket.error as e:
    print(str(e))
print('Socket is listening..')
ServerSideSocket.listen()

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
                online[ID] = connection
                from_to[ID] = None
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
                        online[ID] = connection
                        from_to[ID] = None
                        connection.send(str.encode("Logged in Successfully!"))
                        match = 1
                        f.close()
                        break
                if match == 1:
                    break
                else:
                    connection.send(str.encode("Login failed!"))
                    continue

    print("Users online: ", end="")
    print(online.keys())
    print("Who's sending to whom: ", end="")
    print(from_to)
    while True:
        while True:
            cur.execute('''SELECT * FROM MSGS WHERE RECIPIENT_ID=%s ORDER BY SENDER_ID ASC''',
            (ID, ))
            rows = cur.fetchall()
            cur.execute('''DELETE FROM MSGS WHERE RECIPIENT_ID=%s''',
            (ID, ))
            conn.commit()
            if len(rows) == 0:
                connection.sendall(str.encode("\nNo new messages!"))
                time.sleep(0.1)
                connection.sendall(str.encode(":)"))
            else:
                new_message = "\nYou have " + str(len(rows)) + " new messages!"
                connection.sendall(str.encode(new_message))
                for row in rows:
                    time.sleep(0.1)
                    connection.sendall(str.encode("-> " + row[2] + ": "))
                    time.sleep(0.1)
                    connection.sendall(row[1])
                connection.sendall(str.encode(":)"))      
                
            to_user = connection.recv(2048).decode('utf-8')
            if to_user == "no one":
                online.pop(ID)
                from_to.pop(ID)
                print("Users online: ", end="")
                print(online.keys())
                print("Who's sending to whom: ", end="")
                print(from_to)
                return
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
                cur.execute('''SELECT * FROM KEY WHERE RECIPIENT_ID=%s''',
                (to_user, ))
                connection.sendall(str.encode(cur.fetchone()[1]))
                from_to[ID] = to_user
                cur.execute('''SELECT * FROM MSGS WHERE RECIPIENT_ID=%s AND SENDER_ID=%s''',
                (ID, to_user))
                rows = cur.fetchall()
                cur.execute('''DELETE FROM MSGS WHERE RECIPIENT_ID=%s AND SENDER_ID=%s''',
                (ID, to_user))
                conn.commit()
                if len(rows) == 0:
                    connection.sendall(str.encode("\n********************"))
                    time.sleep(0.1)
                    connection.sendall(str.encode(":)"))
                else:
                    new_message = "\n********************"
                    connection.sendall(str.encode(new_message))
                    for row in rows:
                        time.sleep(0.1)
                        connection.sendall(str.encode("-> " + row[2] + ": "))
                        time.sleep(0.1)
                        connection.sendall(row[1])
                    connection.sendall(str.encode(":)"))
                print("Who's sending to whom: ", end="")
                print(from_to)
                break
            else:
                connection.send(str.encode("This user does not exist!"))
                continue

        while True:
            message = connection.recv(2048)
            if message == str.encode('--'):
                connection.send(message)
                from_to[ID] = None
                print("Who's sending to whom: ", end="")
                print(from_to)
                break
            else:
                if to_user in online.keys():
                    if from_to[to_user] == ID:
                        online[to_user].send(message)
                    else:
                        cur.execute('''INSERT INTO MSGS (RECIPIENT_ID,MSG,SENDER_ID,DURATION) \
                        VALUES (%s, %s, %s, %s);
                        ''',
                        (to_user, psycopg2.Binary(message), ID, duration))
                        conn.commit()

                else:
                    cur.execute('''INSERT INTO MSGS (RECIPIENT_ID,MSG,SENDER_ID,DURATION) \
                    VALUES (%s, %s, %s, %s);
                    ''',
                    (to_user, psycopg2.Binary(message), ID, duration))
                    conn.commit()

while True:
    Client, address = ServerSideSocket.accept()
    print('Connected to: ' + address[0] + ':' + str(address[1]))
    start_new_thread(multi_threaded_client, (Client, ))

ServerSideSocket.close()
