# Connecting to server: telnet 127.0.0.1 2206
# cli is for client, print is for server
# CAN ONLY ACCEPT ONE CLIENT (WHEN LINE 128 AND BELOW IS ENABLED)
# HAVE TO COMMENT OUT FOR MULTIPLE CLIENTS TO CONNECT

import socket, sys, random, string, re # imports multiple library
from _thread import start_new_thread # imports thread library
import threading

versionS = '1.0.1'
systemS = 'Windows 10'
programS = 'Python/3.8'
authorS = "Robert Tung"
ENCODING = 'ascii'
#-------------------------------------------------------------------------#
clients = []
usernameC = ""
usernameS = "Server"
scoreC = 0
scoreS = 0
gameStart = 0
newgame = 0
hellocmd = 0
turn = 0
sturn = 0
cturn = 0
pass_count = 0
word = ""
won = 0
#-------------------------------------------------------------------------#
values = {"a": 1 , "b": 3 , "c": 3 , "d": 2 ,
          "e": 1 , "f": 4 , "g": 2 , "h": 4 ,
          "i": 1 , "j": 8 , "k": 5 , "l": 1 ,
          "m": 3 , "n": 1 , "o": 1 , "p": 3 ,
          "q": 10, "r": 1 , "s": 1 , "t": 1 ,
          "u": 1 , "v": 4 , "w": 4 , "x": 8 ,
          "y": 4 , "z": 10}
grid = []
#-------------------------------------------------------------------------#
port = int(input('Enter listening port number: ')) # default socket port
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # AF_INET refers to address family IPv4 | SOCK_STREAM refers to connection oriented TCP protocol
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try:
    s.bind(('', port)) # '' can contain any address
except socket.error:
    print("Binding failed")
    sys.exit()
s.listen(10) # Number of connections to backlog while waiting
clients = [s]
print(f'Listening for a connection on port {port}... ')

#-------------------------------------------------------------------------#
cli_buffer = b''  # b means "bytestring"--Python is pedantic about differentiating readable text vs a sequence of bytes
cli_lines = []

def cli_read_line(termin=b'\n'):
    global cli_buffer, cli_lines
    try:
        while not cli_lines:  # While there are no input lines...
            data = cli.recv(1024)  # 1024 is the maximum number of bytes to receive
            if not data:  # If data is empty...
                raise EOFError()  #...the connection was closed. Let the caller know.
            cli_buffer = cli_buffer + data
            lines = cli_buffer.split(termin)
            cli_buffer = lines[-1]  # The last element
            cli_lines.extend(lines[:-1])  # Up to the last element
        return cli_lines.pop(0)  # Remove and return the first element
    # except TypeError:
    #     print(f'TypeError Occurred in cli')
    except OSError:
        print(f'Client disconnected from game')
        cli.close()
    except EOFError:
        print(f'Client closed window')
        cli.close()
    except AttributeError:
        print('Recieved unusual attribute')
#-------------------------------------------------------------------------#
def tile_list():
    # Combines two lists into a dictionary and returns a string
    i = 0
    LETTERS = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    COUNT = [2, 4, 9, 14, 9, 7, 1, 14, 7, 3, 11, 10, 8, 14, 14, 4, 4, 15, 14, 8, 2, 3, 4, 7, 10, 1]
    tile_bag = dict(zip(LETTERS, COUNT)) # Creates dictionary of available tiles
    while (i < 2): # Since this version of Scrabble doesn't have "wild" tiles, we distribute 2 extra random letters
        i += 1
        tile_bag[random.choice(string.ascii_uppercase)] += 1
    tiles = [] # Creates a new tile list
    for tile in tile_bag:
        tiles += tile * tile_bag[tile] # Print each letter (key) the amount of times (value) defined in tile_bag
    return tiles
tile_list = tile_list()
#-------------------------------------------------------------------------#
def get_tiles(num):
    # Lists random tiles from tile_list and removes them from tile_list
    count = 0
    tiles = []
    while (count < num):
        tile = random.choice(tile_list)
        index = tile_list.index(tile)
        tiles += tile
        n_tile_list = tile_list.remove(tile)
        count += 1
    return tiles
tilesC = get_tiles(7)
tilesS = get_tiles(7)
def add_tile(num):
    # Lists random tiles from tile_list and removes them from tile_list
    tiles = get_tiles(num)
    count = 0
    while (count < num):
        tile = random.choice(tile_list)
        index = tile_list.index(tile)
        tiles += tile
        n_tile_list = tiles.remove(tile)
        count += 1
    return tiles

#-------------------------------------------------------------------------#
def calc_score(word):
    # Calculate the value of a given word
    word_score = 0
    for x in word.lower():
        word_score += values[x]
    return word_score
hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)

def look_up():
    """Create the variable containing the master list of words."""
    read_dict = open("scrabble_words.txt", "r")
    master = read_dict.read()
    read_dict.close()
    master = master.split("\n")
    return master

word_master = look_up() # Contains a list of dictionary words2

def check_word(word):
    """Check the letters in the rack against the dictionary and
    append valid words to a list."""
    if word in word_master:
        valid = True
    else:
        valid = False
    return valid

while True:
    cli, raddr = s.accept() # Accept connection | If stuck open: lsof -i :{PORT} -> kill -9 [PID]
    cli.sendall(f'Connection successful\n\r'.encode(ENCODING)) # Sends to client
    cli.sendall(f'------------------------------------------------------------------------------------\n\r'.encode(ENCODING))
    cli.sendall(f'OK Welcome to Scrabble! To get started, reply to the HELLO below.\n\r'.encode(ENCODING))
    cli.sendall(f'OK Created by Robert Tung for EE407 Computer Networks.\n\r'.encode(ENCODING))
    cli.sendall(f'OK Using version 1.0.1\n\r'.encode(ENCODING))
    cli.sendall(f'------------------------------------------------------------------------------------\n\r'.encode(ENCODING))
    cli.sendall(f'HELLO {versionS},{systemS},{programS},{authorS}\n\r'.encode(ENCODING)) # Sends to client
    print(f'USERJOIN {raddr[0]}:{raddr[1]}') # Print the USERJOIN to server

    # Does the HELLO command
    try:
        while (hellocmd == 0):
            try:
                ver, sys, prog, auth = cli.recv(1024).decode(ENCODING).split(',') # Split recieved line into 4 parts
                if f"HELLO {versionS}" not in ver: # If HELLO (ver) does not match HELLO (versionS)
                    cli.sendall(f'NOK {ver} is not the correct version, please use the current version: {versionS}\n\r'.replace('HELLO ', '').encode(ENCODING)) # Server response when invalid version is used
                else:
                    print(f'{ver},{sys},{prog},{auth}') # Print the HELLO to server
                    cli.sendall(f'------------------------------------------------------------------------------------\n\r'.encode(ENCODING))
                    cli.sendall(f'OK Please set a username, otherwise you will be known as {IPAddr}\n\r'.encode(ENCODING))
                    cli.sendall(f'OK When you are ready, type READY\n\r'.encode(ENCODING))
                    cli.sendall(f'------------------------------------------------------------------------------------\n\r'.encode(ENCODING))
                    usernameC += IPAddr
                    print(f'OK Waiting for {usernameC} to be ready...')
                    hellocmd = 1
                    break # out of HELLO while loop
            except ValueError:
                # Catches ValueError if the client does not specify enough arguements
                cli.sendall('NOK\n\r'.encode(ENCODING))
            except AttributeError:
                print('Attribute Error')
                break

        while (True and hellocmd == 1):
            game = cli.recv(1024).decode(ENCODING)
            if "QUIT" in game:
                cli.sendall('GOODBYE\n\r'.encode(ENCODING))
                print(f'USERLEAVE {usernameC}')
                cli.close()
            elif "USERSET" in game:
                uset, uname = game.split()
                if (uname != usernameC):
                    print(f'USERCHANGE {usernameC} {uname}') # Print the USERCHANGE to server
                    cli.sendall(f'OK {uname}\n\r'.encode(ENCODING)) # Print the USERCHANGE to client
                    usernameC = uname
                else:
                    cli.sendall(f'NOK Name already taken\n\r'.encode(ENCODING))
                    break
            elif "READY" in game:
                cli.sendall(f'OK Waiting for {usernameS} to be ready...\n\r'.encode(ENCODING))
                ready_check = input(f'{usernameC} is ready to start the game. Type READY when you\'re ready.\n\r')
                if "READY" in ready_check.upper():
                    if (gameStart == 0):
                        cli.sendall('STARTING\n\r'.encode(ENCODING))
                        print(f'STARTING')
                        cli.sendall(f'SCORE {scoreC} {usernameC}\n\r'.encode(ENCODING))
                        print(f'SCORE {scoreC} {usernameS}')
                        print(f'{usernameC} goes first')
                        gameStart = 1
                        newgame = 1
                        break
                    else:
                        cli.sendall('NOK Game already started\n\r'.encode(ENCODING))
                        break
                else:
                    print('OK You have indicated that you are not ready\n\r')
                    cli.sendall(f'NOK {usernameS} is not ready\n\r'.encode(ENCODING))
            else:
                cli.sendall('NOK Unrecognized Command\n\r'.encode(ENCODING))

        while (gameStart == 1):
            if (newgame == 1):
                for row in range(15):
                    grid.append(['*'])
                    for col in range(15):
                        grid[row].append('*')
                newgame = 0
            if (newgame == 0 and turn == 0):
                if (cturn == 0):
                    cli.sendall(f'TILES {tilesC}\n\r'.encode(ENCODING)) # Lists tiles for user
                    cli.sendall(f'TURN {usernameC}\n\r'.encode(ENCODING)) # Sends whose turn it is
                    cli.sendall('BOARDPUSH\n\r'.encode(ENCODING))
                    cli.sendall(f'{grid}\r\n'.replace('[','').replace(']','').replace('\'','').replace(',','').encode(ENCODING))
                    game = cli.recv(1024).decode(ENCODING)
                else:
                    game = cli.recv(1024).decode(ENCODING).upper()
                if "QUIT" in game:
                    cli.sendall('GOODBYE\n\r'.encode(ENCODING))
                    print(f'USERLEAVE {usernameC}')
                    cli.close()
                elif "USERSET" in game:
                    uset, uname = game.split()
                    if (uname != usernameC):
                        print(f'USERSET {usernameC} {uname}') # Print the USERSET to server
                        cli.sendall(f'OK {uname}\n\r'.encode(ENCODING)) # Print the USERCHANGE to client
                        cli.sendall(f'USERCHANGE {usernameC} {uname}\n\r'.encode(ENCODING)) # Print the USERCHANGE to client
                        usernameC = uname
                    else:
                        cli.sendall(f'NOK Name already taken\n\r'.encode(ENCODING))
                        break
                    pass_count = 0
                elif "PLACE" in game:
                    try:
                        count = 0
                        coords = []
                        word_list = []
                        grid_place = game.split()
                        grid_place.remove("PLACE")
                        if (len(grid_place) == 0):
                            raise ValueError()
                        for grid_elem in grid_place:
                            g = re.match("\((.+)\)", grid_elem) # Regex searches for (...)
                            if g:
                                let, stringX, stringY = grid_elem.replace('(','').replace(')','').split(',') # Converts string into list. E.g (A,5,6) -> ['A', '5', '6']
                                word += let.upper() # Stores letters to form the word
                                coords = let, stringX, stringY # Stores letter and coords into list
                                word_list.append(coords)
                        val_word = check_word(word) # Checks if word is in the dictionary. Returns True or False
                        if (val_word == True):
                            for let, stringX, stringY in word_list:
                                if any(let.upper() in tile for tile in tilesC): # If client has tile in their rack
                                    x = int(stringX) # Convert string to int
                                    y = int(stringY)
                                    if '*' in grid[x][y]: # If there is a * in the placed location
                                        grid[x][y] = let.upper() # Set row x, column y to letter
                                        tilesC.remove(let)
                                        # grid_multiple(x,y)
                                        scoreC += calc_score(let) # Update client score
                                        count += 1
                                    else:
                                        cli.sendall(f'NOK Location {x},{y} already has a letter. Not placed.\n\r'.encode(ENCODING))
                                else:
                                    cli.sendall(f'NOK {let} is not in available tiles. Not placed.\n\r'.encode(ENCODING))
                            tilesC += add_tile(count)
                            cli.sendall(f'{grid}\r\n'.replace('[','').replace(']','').replace('\'','').replace(',','').encode(ENCODING))
                            cli.sendall(f'OK Turn Successful\n\r'.encode(ENCODING))
                            cli.sendall(f'SCORE {scoreC} {usernameC}\n\r'.encode(ENCODING))
                            cli.sendall(f"TURN {usernameS}\n\r".encode(ENCODING))
                        elif (val_word == False):
                            cli.sendall(f'{grid}\r\n'.replace('[','').replace(']','').replace('\'','').replace(',','').encode(ENCODING))
                            cli.sendall(f'NOK Invalid word sent.\n\r'.encode(ENCODING))
                        word = ""
                        pass_count = 0
                        turn = 1
                    except ValueError:
                        cli.sendall('NOK Invalid amount of parameters sent\n\r'.encode(ENCODING))
                elif "EXCHANGE" in game:
                    try:
                        count = 0
                        invalid = []
                        valid = []
                        let_list = game.split()
                        let_list.remove("EXCHANGE")
                        if (len(let_list) == 0):
                            raise ValueError()
                        for let in let_list:
                            if any(let.upper() in tile for tile in tilesC):
                                tilesC.remove(let)
                                count += 1
                                valid += let
                            else:
                                invalid += let
                        if (len(invalid) > 0):
                            cli.sendall(f'NOK {invalid} not in your tiles\n\r'.encode(ENCODING))
                        if (count > 0):
                            tilesC += add_tile(count)
                            cli.sendall(f'OK {valid} exchanged\n\r'.encode(ENCODING))
                        cli.sendall(f'TILES {tilesC}\n\r'.encode(ENCODING))
                        cli.sendall(f'SCORE {scoreC} {usernameC}\n\r'.encode(ENCODING))
                        cli.sendall(f"TURN {usernameS}\n\r".encode(ENCODING))
                        turn = 1
                    except ValueError:
                        cli.sendall('NOK Invalid amount of parameters sent\n\r'.encode(ENCODING))
                elif "TILES" in game:
                    cli.sendall(f'{tilesC}\n\r'.encode(ENCODING))
                    pass_count = 0
                elif "PASS" in game:
                    pass_count += 1
                    print(f'PASS {usernameC}\n\r')
                    if (pass_count == 2):
                        if (scoreC > scoreS):
                            print(f'WINNER {usernameC} {scoreC}\n\r')
                            cli.sendall(f'WINNER {usernameC} {scoreC}\n\r'.encode(ENCODING))
                            cli.sendall(f'Please send the QUIT command to leave\n\r'.encode(ENCODING))
                            won = 1
                            break
                        elif (scoreS > scoreC):
                            print(f'WINNER {usernameS} {scoreS}\n\r')
                            cli.sendall(f'WINNER {usernameS} {scoreS}\n\r'.encode(ENCODING))
                            cli.sendall(f'Please send the QUIT command to leave\n\r'.encode(ENCODING))
                            won = 1
                            break
                    turn = 1
                else:
                    cli.sendall('NOK Unrecognized Command\n\r'.encode(ENCODING))

            if (newgame == 0 and turn == 1):
                if (sturn == 0):
                    print(f'TILES {tilesS}\n\r') # Lists tiles for user
                    print(f'TURN {usernameC}\n\r') # Sends whose turn it is
                    print('BOARDPUSH\n\r')
                    print(f'{grid}\r\n'.replace('[','').replace(']','').replace('\'','').replace(',','')) #
                    sgame = input(f"TURN {usernameS}\n\r")
                    sturn = 1
                else:
                    sgame = input(f"TURN {usernameS}\n\r")
                if "PLACE" in sgame.upper():
                    try:
                        count = 0
                        coords = []
                        word_list = []
                        grid_place = sgame.split()
                        grid_place.remove("PLACE")
                        if (len(grid_place) == 0):
                            raise ValueError()
                        for grid_elem in grid_place:
                            g = re.match("\((.+)\)", grid_elem) # Regex searches for (...)
                            if g:
                                let, stringX, stringY = grid_elem.replace('(','').replace(')','').split(',') # Converts string into list. E.g (A,5,6) -> ['A', '5', '6']
                                word += let.upper() # Stores letters to form the word
                                coords = let, stringX, stringY # Stores letter and coords into list
                                word_list.append(coords)
                        val_word = check_word(word) # Checks if word is in the dictionary. Returns True or False
                        if (val_word == True):
                            for let, stringX, stringY in word_list:
                                if any(let.upper() in tile for tile in tilesS): # If client has tile in their rack
                                    x = int(stringX) # Convert string to int
                                    y = int(stringY)
                                    if '*' in grid[x][y]: # If there is a * in the placed location
                                        grid[x][y] = let.upper() # Set row x, column y to letter
                                        tilesS.remove(let)
                                        # grid_multiple(x,y)
                                        scoreS += calc_score(let) # Update client score
                                        count += 1
                                    else:
                                        print(f'NOK Location {x},{y} already has a letter. Not placed.\n\r'.encode(ENCODING))
                                else:
                                    print(f'NOK {let} is not in available tiles. Not placed.\n\r'.encode(ENCODING))
                            tilesS += add_tile(count)
                            print(f'{grid}\r\n'.replace('[','').replace(']','').replace('\'','').replace(',',''))
                            print(f'OK Turn Successful\n\r')
                            print(f'SCORE {scoreS} {usernameS}\n\r')
                        elif (val_word == False):
                            print(f'{grid}\r\n'.replace('[','').replace(']','').replace('\'','').replace(',',''))
                            print(f'NOK Invalid word sent.\n\r')
                        word = ""
                        pass_count = 0
                        turn = 0
                    except ValueError:
                        print('NOK Invalid amount of parameters sent\n\r')
                elif "EXCHANGE" in sgame.upper():
                    try:
                        count = 0
                        invalid = []
                        valid = []
                        let_list = game.split()
                        let_list.remove("EXCHANGE")
                        if (len(let_list) == 0):
                            raise ValueError()
                        for let in let_list:
                            if any(let.upper() in tile for tile in tilesS):
                                tilesS.remove(let)
                                count += 1
                                valid += let
                            else:
                                invalid += let
                        if (len(invalid) > 0):
                            print(f'NOK {invalid} not in your tiles\n\r')
                        if (count > 0):
                            tilesS += add_tile(count)
                            print(f'OK {valid} exchanged\n\r')
                        print(f'TILES {tilesS}\n\r')
                        print(f'SCORE {scoreS} {usernameS}\n\r')
                        print(f"TURN {usernameC}\n\r")
                        turn = 0
                    except ValueError:
                        print('NOK Invalid amount of parameters sent\n\r'.encode(ENCODING))
                elif "TILES" in sgame.upper():
                    print(f'{tilesS}\n\r')
                    pass_count = 0
                elif "PASS" in sgame.upper():
                    pass_count += 1
                    cli.sendall(f'PASS {usernameC}\n\r'.encode(ENCODING))
                    if (pass_count == 2):
                        if (scoreC > scoreS):
                            print(f'WINNER {usernameC} {scoreC}\n\r')
                            cli.sendall(f'WINNER {usernameC} {scoreC}\n\r'.encode(ENCODING))
                            cli.sendall(f'Please send the QUIT command to leave\n\r'.encode(ENCODING))
                            won = 1
                            break
                        elif (scoreS > scoreC):
                            print(f'WINNER {usernameS} {scoreS}\n\r')
                            cli.sendall(f'WINNER {usernameS} {scoreS}\n\r'.encode(ENCODING))
                            cli.sendall(f'Please send the QUIT command to leave\n\r'.encode(ENCODING))
                            won = 1
                            break
                    cli.sendall(f"TURN {usernameC}")
                    turn = 0
                else:
                    print('NOK Unrecognized Command\n\r')
        if (won == 1):
            while True:
                try:
                    endgame = cli_read_line().decode(ENCODING).upper()
                    if "QUIT" in endgame:
                        cli.sendall('GOODBYE\n\r'.encode(ENCODING))
                        print(f'USERLEAVE {usernameC}')
                        cli.close()
                        break
                    else:
                        continue
                except AttributeError:
                    print(f'Recieved unusual attribute')
                    break
    except AttributeError:
        print()
    except TypeError:
        print(f'TypeError Occurred in cli')
    except OSError:
        print(f'Client disconnected from game')
cli.close()
