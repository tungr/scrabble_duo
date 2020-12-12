# Connecting to server: telnet 127.0.0.1 2206
# cli is for client, print is for server
# CAN ONLY ACCEPT ONE CLIENT (WHEN LINE 128 AND BELOW IS ENABLED)
# HAVE TO COMMENT OUT FOR MULTIPLE CLIENTS TO CONNECT

import socket, sys # imports multiple library
from time import sleep
from _thread import start_new_thread # imports thread library
import threading

versionC = '1.0.1'
systemC = ''
programC = 'Python/3.8'
authorC = ''
ENCODING = 'ascii'

hellocheck = 0
namecheck = 0
readycheck = 0
extracheck = 0
netcheck = 0
activegame = 0

data = b''  # recv() does return bytes
chunk = b''

host = input('Enter listening host (IP)\n\r> ')  # The server's hostname or IP address
port = int(input('Enter listening port number\n\r> ')) # default socket port

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
except ConnectionRefusedError:
    print('The IP and port you tried connecting to does not have anything active on it.')
    sys.exit()
while not authorC:
    authorC = input('What is your name?\n\r> ')
while not systemC:
    systemC = input('What system are you using? (Windows, Linux, etc.)\n\r> ')

while True:
    try:
        # while True:
        # # while not chunk:
        #     try:
        #         chunk = s.recv(1024)
        #         if not chunk:
        #             break
        #         data += chunk
        #     except socket.error:
        #         s.close()
        #         break
        sleep(0.5)
        data = s.recv(1024)
        print(data.decode(ENCODING))

        while (hellocheck == 0):
            entry = input('Please type HELLO when ready\n\r> ')
            if "HELLO" in entry.upper():
                s.sendall(f'HELLO {versionC},{systemC},{programC},{authorC}'.encode(ENCODING))
                hellocheck = 1
            else:
                s.sendall(entry.encode(ENCODING))
        while ((namecheck == 0) and (hellocheck == 1)):
            sleep(0.5)
            data = s.recv(1024)
            print(data.decode(ENCODING))
            nameque = input('Do you want to set a username? (Y/N)\n\r> ')
            if 'Y' in nameque.upper():
                username = input('Set a username\n\r> ')
                s.sendall(f'USERSET {username}'.encode(ENCODING))
                namecheck = 1
                break
            elif 'N' in nameque.upper():
                namecheck = 1
                break
            else:
                s.sendall(entry.encode(ENCODING))
                namecheck = 0
        while ((readycheck == 0) and (namecheck == 1)):
            readyque = input('Are you ready to start? (Y/N)\n\r> ')
            if ('Y') in readyque.upper():
                s.sendall('READY'.encode(ENCODING))
                readycheck = 1
                activegame = 1
                break
            elif ('N') in readyque.upper():
                print('When you are ready, type below')
                readycheck = 0
            else:
                readycheck = 0
        while (activegame == 1):
            sleep(0.5)
            data = s.recv(1024)
            print(data.decode(ENCODING))
            if (extracheck == 0):
                print('TIP: To PLACE pieces: type a letter, x-axis, and y-axis such as (A, 1, 2)')
                print('Use a space in between to place more pieces')
                print('Example: (A,1,2) (B,2,3)')
                print('TIP: To REPLACE pieces: type a letter with a space in between such as REPLACE A B C')
                print('TIP: Type PASS if you want to pass')
                extracheck = 1
                break
            while (extracheck == 1):
                if (netcheck == 1):
                    sleep(0.5)
                    data = s.recv(1024)
                    print(data.decode(ENCODING))
                place = input('\n\r> ')
                if "PASS" in place.upper():
                    s.sendall('PASS'.encode(ENCODING))
                elif "REPLACE" in place.upper():
                    s.sendall(f'REPLACE {place}'.encode(ENCODING))
                else:
                    s.sendall(f'PLACE {place}'.encode(ENCODING))
                netcheck = 1
    except OSError:
        print('Data could not be sent.')
        sys.exit()
