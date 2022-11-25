import socket
import os
import psycopg2
import time
from _thread import *
import threading

def client_to_LB(ID, to_user):
    while True:
        connection = online[ID]
        message = connection.recv(2048)
        if message == str.encode('--'):
            time.sleep(0.1)
            ConnectToLB.send(str.encode(ID + "|" + ID))
            time.sleep(0.1)
            ConnectToLB.send(message)
            return
        elif to_user in online.keys():
            cur.execute('''SELECT * FROM FROMTO WHERE SENDER_ID=%s''',
                (to_user, ))
            row = cur.fetchone()
            if row[1] == ID:
                online[to_user].send(message)
            else:
                cur.execute('''INSERT INTO MSGS (RECIPIENT_ID, MSG, SENDER_ID, DURATION) \
                    VALUES (%s, %s, %s, %s);
                    ''',
                    (to_user, psycopg2.Binary(message), ID, duration))
                conn.commit()            
        else:
            time.sleep(0.1)
            ConnectToLB.send(str.encode(ID + "|" + to_user))
            time.sleep(0.2)
            ConnectToLB.send(message)

def LB_to_client():
    while True:
        t = ConnectToLB.recv(2048).decode('utf-8')
        message = ConnectToLB.recv(2048)
        if t.startswith('<'):
            g_f_t = t.split('-')
            online[g_f_t[2]].send(str.encode(g_f_t[1]+"|"+message.decode('utf-8')))
        else:
            online[t].send(message)
        if message == str.encode('--'):
            cur.execute('''UPDATE FROMTO
                SET RECIPIENT_ID= '####'
                WHERE SENDER_ID=%s''',
                (t, ))
            return

ServerSideSocket = socket.socket()
host = '127.0.0.1'
port = 4004
online = {}
duration = 0

ConnectToLB = socket.socket()
print('Waiting for connection response')
try:
    ConnectToLB.connect((host, 2004))
except socket.error as e:
    print(str(e))

conn = psycopg2.connect(database="store", user="param")
cur = conn.cursor()

try:
    ServerSideSocket.bind((host, port))
except socket.error as e:
    print(str(e))
print('Socket is listening..')
ServerSideSocket.listen()

def multi_threaded_client(connection):

    ID = connection.recv(2048).decode('utf-8')
    online[ID] = connection
    cur.execute('''INSERT INTO FROMTO (SENDER_ID, RECIPIENT_ID) \
        VALUES(%s, '####');
        ''',
        (ID, ))
    conn.commit()
    print("Users online: ", end="")
    print(online.keys())
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

            if to_user.startswith("#CG"):
                items = to_user.split('-', 2)
                name = items[1]
                members = items[2]
                match = 1
                cur.execute('''SELECT * FROM KEY''')
                rows = cur.fetchall()
                signs = [i[0] for i in rows]
                for member in members.split('-'):
                    if not (member in signs):
                        match = 0
                if not (name.startswith('<') and name.endswith('>')):
                    connection.send(str.encode("Group name must be enclosed in angular brackets!"))
                    continue
                if match == 0:
                    connection.send(str.encode("Some users do not exist!"))
                    continue
                cur.execute('''INSERT INTO GROUPS (NAME, MEMBERS) \
                    VALUES (%s, %s)''',
                    (name, members))
                join_msg = ID+" added you to "+items[1]+" with members: "+members.replace('-', ', ')
                for member in members.split('-'):
                    cur.execute('''INSERT INTO MSGS (RECIPIENT_ID, MSG, SENDER_ID, DURATION) \
                        VALUES (%s, %s, '#A', %s)''',
                        (member, join_msg, duration))
                conn.commit()
                to_user = name
                connection.send(str.encode("********************"))
                time.sleep(0.1)
                connection.send(str.encode("\n********************"))
                time.sleep(0.1)
                connection.send(str.encode(":)"))
                cur.execute('''UPDATE FROMTO
                    SET RECIPIENT_ID=%s
                    WHERE SENDER_ID=%s''',
                    (to_user, ID))
                conn.commit()
                break
                

            elif to_user.startswith("<"):
                cur.execute('''SELECT * FROM GROUPS''')
                rows = cur.fetchall()
                names = [i[0] for i in rows]
                if not to_user in names:
                    connection.send(str.encode("This group does not exist!"))
                    continue
                else:
                    connection.send(str.encode("********************"))
                    cur.execute('''UPDATE FROMTO
                    SET RECIPIENT_ID=%s
                    WHERE SENDER_ID=%s''',
                    (to_user, ID))
                    cur.execute('''SELECT * FROM MSGS WHERE RECIPIENT_ID=%s''',
                    (ID, ))
                    rows = cur.fetchall()
                    messages = []
                    for row in rows:
                        if row[2].startswith(to_user):
                            messages.append(row)
                    cur.execute('''SELECT * FROM GROUPS WHERE NAME=%s''',
                        (to_user, ))
                    members = cur.fetchone()[1].split('-')
                    for member in members:
                        cur.execute('''DELETE FROM MSGS WHERE RECIPIENT_ID=%s and SENDER_ID=%s''',
                        (ID, to_user+'-'+member))
                    conn.commit()
                    if len(messages) == 0:
                        connection.sendall(str.encode("\n********************"))
                        time.sleep(0.1)
                        connection.sendall(str.encode(":)"))
                    else:
                        new_message = "\n********************"
                        connection.sendall(str.encode(new_message))
                        for row in rows:
                            time.sleep(0.1)
                            connection.sendall(str.encode("-> " + messages[2] + ": "))
                            time.sleep(0.1)
                            connection.sendall(messages[1])
                        connection.sendall(str.encode(":)"))
                    break


            elif to_user == "no one":
                online.pop(ID)
                cur.execute('''DELETE FROM FROMTO WHERE SENDER_ID=%s''',
                (ID, ))
                cur.execute('''DELETE FROM CLIENTS WHERE ID=%s''',
                (ID, ))
                cur.execute('''SELECT * FROM CC WHERE SERVER_NUMBER=4''')
                count = cur.fetchone()[1]-1
                cur.execute('''UPDATE CC
                    SET COUNT=%s
                    WHERE SERVER_NUMBER=4''',
                    (count, ))
                conn.commit()
                print("Users online: ", end="")
                print(online.keys())
                return
            
            else:
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
                    cur.execute('''UPDATE FROMTO
                    SET RECIPIENT_ID=%s
                    WHERE SENDER_ID=%s''',
                    (to_user, ID))
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
                    break
                else:
                    connection.send(str.encode("This user does not exist!"))
                    continue

        t1 = threading.Thread(target=client_to_LB, args=[ID, to_user])
        t1.start()
        LB_to_client()
        t1.join()

while True:
    Client, address = ServerSideSocket.accept()
    print('Connected to: ' + address[0] + ':' + str(address[1]))
    start_new_thread(multi_threaded_client, (Client, ))

conn.close()
ServerSideSocket.close()
