import socket
import os
from _thread import *
import psycopg2


ServerSideSocket = socket.socket()
host = '127.0.0.1'
port = 2004
online = {}
from_to = {}
time = 0

conn = psycopg2.connect(database = "messages", user = "param")
print("Opened database successfully")

cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS MSGS")
cur.execute('''CREATE TABLE MSGS
      (RECIPIENT_ID TEXT     NOT NULL,
      MSG           TEXT    NOT NULL,
      SENDER_ID            TEXT     NOT NULL,
      DURATION         REAL);''')
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
            if len(rows) == 0:
                connection.send(str.encode("No new messages!"))
            else:
                new_messages = "\nYou have " + str(len(rows)) + " new messages!\n"
                for row in rows:
                    new_messages += "\n-> " + row[2] + ": " + row[1]
                connection.send(str.encode(new_messages))
                
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
                from_to[ID] = to_user
                cur.execute('''SELECT * FROM MSGS WHERE RECIPIENT_ID=%s ORDER BY SENDER_ID ASC''',
                (ID, ))
                rows = cur.fetchall()
                cur.execute('''DELETE FROM MSGS WHERE RECIPIENT_ID=%s''',
                (ID, ))
                if len(rows) == 0:
                    connection.send(str.encode("********************"))
                else:
                    new_messages = "********************\n"
                    for row in rows:
                        new_messages += "\n-> " + row[2] + ": " + row[1]
                    connection.send(str.encode(new_messages))
                print("Who's sending to whom: ", end="")
                print(from_to)
                break
            else:
                connection.send(str.encode("This user does not exist!"))
                continue

        while True:
            message = connection.recv(2048).decode('utf-8')
            if message == '--':
                connection.send(str.encode(message))
                from_to[ID] = None
                print("Who's sending to whom: ", end="")
                print(from_to)
                break
            else:
                if to_user in online.keys():
                    if from_to[to_user] == ID:
                        online[to_user].send(str.encode(message))
                    else:
                        cur.execute('''INSERT INTO MSGS (RECIPIENT_ID,MSG,SENDER_ID,DURATION) \
                        VALUES (%s, %s, %s, %s);
                        ''',
                        (to_user, message, ID, time))
                        conn.commit()

                else:
                    cur.execute('''INSERT INTO MSGS (RECIPIENT_ID,MSG,SENDER_ID,DURATION) \
                    VALUES (%s, %s, %s, %s);
                    ''',
                    (to_user, message, ID, time))
                    conn.commit()

while True:
    Client, address = ServerSideSocket.accept()
    print('Connected to: ' + address[0] + ':' + str(address[1]))
    start_new_thread(multi_threaded_client, (Client, ))

ServerSideSocket.close()
