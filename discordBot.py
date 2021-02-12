#Python Programming Final Project - Discord Bot
#Casey Schablein, Timothy Neale, Robert Deal

import discord
import random

client = discord.Client()

commands = ["help","[]d[]", "diceTotal", "diceGame","chess start","chess move [start] [end]","chess end","c4 help","c4 reset","c4 blu [val]","c4 red [val]","c4 help"] ##keep a list of any commands you can give to the bot here, will be printed for the help command

users = [] ##these lists keep track of everyones dice rolls, see function addRoll()
lastUsed = []
numRolls = []
diceTotal = []
nat20 = []
nat1 = []

#defines chess pieces as unicode emojis for easier display
wrook = '♖'
wbishop = '♗'
wknight = '♘'
wpawn = '♙'
wqueen = '♕'
wking = '♔'
white_pieces = [wrook, wbishop, wknight, wpawn, wqueen, wking]

brook = '♜'
bbishop = '♝'
bknight = '♞'
bpawn = '♟'
bqueen = '♛'
bking = '♚'
black_pieces = [brook, bbishop, bknight, bpawn, bqueen, bking]

space = str(chr(32))

grid = []

#dict of active chess games for each channel it is used in
chess_games = {}


def diceRoll(numSides):
    result = random.randrange(numSides) + 1
    return result

def addRoll(user, roll, numSides): ##This function keeps track of everyones individual rolls, keeping number of rolls, totals, and last die rolled
    if(user not in users):
        print("Adding user: " + str(user)) ##here it makes sure a user is already in the list, if not, add them
        users.append(user)
        lastUsed.append(0)
        numRolls.append(0)
        diceTotal.append(0)
        nat20.append(0)
        nat1.append(0)

    lastUsed[users.index(user)] = numSides
    numRolls[users.index(user)] = numRolls[users.index(user)] + 1
    diceTotal[users.index(user)] = diceTotal[users.index(user)] + roll

    if(roll == 20 and numSides == 20):
        nat20[users.index(user)] = nat20[users.index(user)] + 1   ##This function also keeps track of any natural 20's and natural 1's only rolled on d20s
    if(roll == 1 and numSides == 20):
        nat1[users.index(user)] = nat1[users.index(user)] + 1

def compareHands(player, dealer): ##this functions determines the winner of the poker game, giving more points if you have a pair, more for two pair, and then a ton more for a straight
    playersPoints = 0
    playerPairs = 1
    dealerPoints = 0
    dealerPairs = 1
    for x in range(1,9):
        if(player.count(x) > 1):
            playersPoints = playersPoints + pow(x*player.count(x),playerPairs)  ##pairs
            playerPairs = playerPairs + 1

        if(sorted(player)[3] - sorted(player)[0] == 3):
            playersPoints = playersPoints + (sorted(player)[3]*sorted(player)[3]) + 5000 ##straight

        if(dealer.count(x) > 1): ##does the same thing as the player but for the dealer
            dealerPoints = dealerPoints + pow(x*dealer.count(x),dealerPairs)
            dealerPairs = dealerPairs + 1
        if(sorted(dealer)[3] - sorted(dealer)[0] == 3):
            dealerPoints = dealerPoints + (sorted(dealer)[3]*sorted(dealer)[3]) + 5000

        if(dealerPoints == playersPoints):
            playersPoints = playersPoints + (max(player) - max(dealer)) ##adds difference between the highs in each hand in case of no other points
    return (playersPoints > dealerPoints) ##returns true if player won


#returns 2d array of all starting spaces in chessboard
def newChess():
    return [[brook,bknight,bbishop,bqueen,bking,bbishop,bknight,brook],
            [bpawn,bpawn,bpawn,bpawn,bpawn,bpawn,bpawn,bpawn],
            ['','','','','','','',''],
            ['','','','','','','',''],
            ['','','','','','','',''],
            ['','','','','','','',''],
            [wpawn,wpawn,wpawn,wpawn,wpawn,wpawn,wpawn,wpawn],
            [wrook,wknight,wbishop,wqueen,wking,wbishop,wknight,wrook]]

#returns string to print chessboard given channel name
def printChess(channel):
    board = '`'
    col = '8'
    for i in chess_games[channel]:
        board = board + col + space + '|'
        col = str(chr(ord(col) - 1))
        for j in i:
            if j == '':
                board += space + space + space + space + '|'
            else:
                board += space + j + space + '|'
        board += '\n'
    board += '    A    B    C    D    E    F    G    H `'
    return board
                
#Function to see if moving a piece from start to end is valid, then move piece if valid
def movePiece(chess_games,channel, start, end):
    #Assumes call is within valid chess parameters, as called from valid $chess move command
    piece = chess_games[channel][start[0]][start[1]]

    #Sets prefixes to determine logic for moving pieces
    if piece == wpawn or piece == wknight or piece == wbishop or piece == wrook or piece == wking or piece == wqueen:
        prefix = 'w'
    elif piece == bpawn or piece == bknight or piece == bbishop or piece == brook or piece == bking or piece == bqueen:
        prefix = 'b'
    else:
        prefix = ''

    end_piece = chess_games[channel][end[0]][end[1]]

    if end_piece == wpawn or end_piece == wknight or end_piece == wbishop or end_piece == wrook or end_piece == wking or end_piece == wqueen:
        end_prefix = 'w'
    elif end_piece == bpawn or end_piece == bknight or end_piece == bbishop or end_piece == brook or end_piece == bking or end_piece == bqueen:
        end_prefix = 'b'
    else:
        end_prefix = ''

    
    if prefix == '' or prefix == end_prefix or (start[0] == end[0] and start[1] == end[1]):
        return 0
    
    #Conditions for moving pawn piece
    elif piece == bpawn or piece == wpawn:
        if end_prefix == '' and prefix == 'w':
            if end[0] < start[0] and (end[0] - start[0] >= -1 or (end[0] - start[0] == -2 and start[0] == 6 and chess_games[channel][end[0]+1][start[1]] == '')) and end[1] == start[1]:
                chess_games[channel][end[0]][end[1]] = wpawn
                if end[0] == 0:
                    chess_games[channel][end[0]][end[1]] = wqueen
                chess_games[channel][start[0]][start[1]] = ''
                return 1
            else:
                return 0
        elif end_prefix == '' and prefix == 'b':
            if end[0] > start[0] and (end[0] - start[0] <= 1 or (end[0] - start[0] == 2 and start[0] == 1 and chess_games[channel][end[0]-1][start[1]] == '')) and end[1] == start[1]:
                chess_games[channel][end[0]][end[1]] = bpawn
                if end[0] == 7:
                    chess_games[channel][end[0]][end[1]] = bqueen
                chess_games[channel][start[0]][start[1]] = ''
                return 1
            else:
                return 0
        elif prefix == 'w':
            if end[0] - start[0] == -1 and abs(end[1] - start[1]) == 1:
                chess_games[channel][end[0]][end[1]] = wpawn
                if end[0] == 0:
                    chess_games[channel][end[0]][end[1]] = wqueen
                chess_games[channel][start[0]][start[1]] = ''
                return 1
            else:
                return 0
                                
        elif prefix == 'b':
            if end[0] - start[0] == 1 and abs(end[1] - start[1]) == 1:
                chess_games[channel][end[0]][end[1]] = bpawn
                if end[0] == 7:
                    chess_games[channel][end[0]][end[1]] = bqueen
                chess_games[channel][start[0]][start[1]] = ''
                return 1
            else:
                return 0
        else:
            return 0

    #conditions for moving knight piece
    elif piece == bknight or piece == wknight:
        if (abs(start[0] - end[0]) == 2 and abs(start[1] - end[1]) == 1) or (abs(start[0] - end[0]) == 1 and abs(start[1] - end[1]) == 2):
            if prefix == 'b':
                chess_games[channel][end[0]][end[1]] = bknight
            else:
                chess_games[channel][end[0]][end[1]] = wknight
            chess_games[channel][start[0]][start[1]] = ''
            return 1
        else:
            return 0

    #conditions for moving rook piece
    elif piece == brook or piece == wrook:
        if start[0] != end[0] and start[1] != end[1]:
            return 0
        elif start[0] == end[0]:
            for i in range(min(start[1],end[1]) + 1, max(start[1],end[1])):
                if chess_games[channel][start[0]][i] != '':
                    return 0
            chess_games[channel][end[0]][end[1]] = piece
            chess_games[channel][start[0]][start[1]] = ''
            return 1
        elif start[1] == end[1]:
            for i in range(min(start[0],end[0]) + 1, max(start[0],end[0])):
                if chess_games[channel][i][start[1]] != '':
                    return 0
            chess_games[channel][end[0]][end[1]] = piece
            chess_games[channel][start[0]][start[1]] = ''
            return 1
        else:
            return 0

    #conditions for moving bishop piece
    elif piece == bbishop or piece == wbishop:
        if abs(start[0] - end[0]) != abs(start[1] - end[1]):
            return 0
        elif start[0] - end[0] != start[1] - end[1]:
            for i in range(1,max(start[0],end[0])-min(start[0],end[0])):
                print(min(start[0],end[0])+i)
                print(max(start[1],end[1])-i)
                if chess_games[channel][min(start[0],end[0])+i][max(start[1],end[1])-i] != '':
                    return 0
            chess_games[channel][end[0]][end[1]] = piece
            chess_games[channel][start[0]][start[1]] = ''
            return 1
        else:
            for i in range(1,max(start[0],end[0])-min(start[0],end[0])):
                if chess_games[channel][min(start[0],end[0])+i][min(start[1],end[1])+i] != '':
                    return 0
            chess_games[channel][end[0]][end[1]] = piece
            chess_games[channel][start[0]][start[1]] = ''
            return 1

    #conditions for moving queen - conditionally uses code from rook/bishop
    elif piece == bqueen or piece == wqueen:
        if (abs(start[0] - end[0]) == abs(start[1] - end[1])):
            if start[0] - end[0] != start[1] - end[1]:
                for i in range(1,max(start[0],end[0])-min(start[0],end[0])):
                    print(min(start[0],end[0])+i)
                    print(max(start[1],end[1])-i)
                    if chess_games[channel][min(start[0],end[0])+i][max(start[1],end[1])-i] != '':
                        return 0
                chess_games[channel][end[0]][end[1]] = piece
                chess_games[channel][start[0]][start[1]] = ''
                return 1
            else:
                for i in range(1,max(start[0],end[0])-min(start[0],end[0])):
                    if chess_games[channel][min(start[0],end[0])+i][min(start[1],end[1])+i] != '':
                        return 0
                chess_games[channel][end[0]][end[1]] = piece
                chess_games[channel][start[0]][start[1]] = ''
                return 1
        elif (start[0] == end[0]) != (start[1] == end[1]):
            if start[0] == end[0]:
                for i in range(min(start[1],end[1]) + 1, max(start[1],end[1])):
                    if chess_games[channel][start[0]][i] != '':
                        return 0
                chess_games[channel][end[0]][end[1]] = piece
                chess_games[channel][start[0]][start[1]] = ''
                return 1
            elif start[1] == end[1]:
                for i in range(min(start[0],end[0]) + 1, max(start[0],end[0])):
                    if chess_games[channel][i][start[1]] != '':
                        return 0
                chess_games[channel][end[0]][end[1]] = piece
                chess_games[channel][start[0]][start[1]] = ''
                return 1
        else:
            return 0

    #conditions for moving king piece
    elif piece == bking or piece == wking:
        if abs(start[0] - end[0]) > 1 or abs(start[1] - end[1]) > 1:
            return 0
        else:
            chess_games[channel][end[0]][end[1]] = piece
            chess_games[channel][start[0]][start[1]] = ''
            return 1

    else:
        return 0


#Function for using emojis in connect four     
def emoji(inp):
    if inp == 0:
        return ':black_square_button:'
    if inp == 1:
        return ':large_blue_circle:'
    if inp == 2:
        return ':red_circle:'

#Shows grid for connect four          
def showGrid(win):
    global grid
    grid_pic = 'Connect Four:\n'
    grid_pic = grid_pic + ':one: :two: :three: :four: :five: :six: :seven:\n'
    grid_pic = grid_pic + emoji(grid[0][5]) + ' ' + emoji(grid[1][5]) + ' ' + emoji(grid[2][5]) + ' ' + emoji(grid[3][5]) + ' ' + emoji(grid[4][5]) + ' ' + emoji(grid[5][5]) + ' ' + emoji(grid[6][5]) + '\n'
    grid_pic = grid_pic + emoji(grid[0][4]) + ' ' + emoji(grid[1][4]) + ' ' + emoji(grid[2][4]) + ' ' + emoji(grid[3][4]) + ' ' + emoji(grid[4][4]) + ' ' + emoji(grid[5][4]) + ' ' + emoji(grid[6][4]) + '\n'
    grid_pic = grid_pic + emoji(grid[0][3]) + ' ' + emoji(grid[1][3]) + ' ' + emoji(grid[2][3]) + ' ' + emoji(grid[3][3]) + ' ' + emoji(grid[4][3]) + ' ' + emoji(grid[5][3]) + ' ' + emoji(grid[6][3]) + '\n'
    grid_pic = grid_pic + emoji(grid[0][2]) + ' ' + emoji(grid[1][2]) + ' ' + emoji(grid[2][2]) + ' ' + emoji(grid[3][2]) + ' ' + emoji(grid[4][2]) + ' ' + emoji(grid[5][2]) + ' ' + emoji(grid[6][2]) + '\n'
    grid_pic = grid_pic + emoji(grid[0][1]) + ' ' + emoji(grid[1][1]) + ' ' + emoji(grid[2][1]) + ' ' + emoji(grid[3][1]) + ' ' + emoji(grid[4][1]) + ' ' + emoji(grid[5][1]) + ' ' + emoji(grid[6][1]) + '\n'
    grid_pic = grid_pic + emoji(grid[0][0]) + ' ' + emoji(grid[1][0]) + ' ' + emoji(grid[2][0]) + ' ' + emoji(grid[3][0]) + ' ' + emoji(grid[4][0]) + ' ' + emoji(grid[5][0]) + ' ' + emoji(grid[6][0]) + '\n'
    if win:
        grid_pic = grid_pic + "Congratulations, you win!!!\n"
        grid = [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]]
    
    return grid_pic

#Adds piece in connect four
def addPuck(column, color):
    global grid
    try:
        grid[column][grid[column].index(0)] = color
        return showGrid(anyoneWin(color))
    except:
        return 'Please try a different column'

#checks if winner in connect four
def anyoneWin(c):
    global grid
    
    #checks horizontals
    for x in range(4):
        for y in range(6):
            if grid[x][y] == c and grid[x+1][y] == c and grid[x+2][y] == c and grid[x+3][y] == c:
                return True

    #checks verticals
    for x in range(7):
        for y in range(3):
            if grid[x][y] == c and grid[x][y+1] == c and grid[x][y+2] == c and grid[x][y+3] == c:
                return True

    #checks diagonal
    for x in range(4):
        for y in range(3, 6):
            if grid[x][y] == c and grid[x-1][y+1] == c and grid[x-2][y+2] == c and grid[x-3][y+3] == c:
                return True
    return False


#Code based on starter code from https://discordpy.readthedocs.io/en/rewrite/quickstart.html
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    msg = message.content.lower() ##lowers message to keep things consistent and make sure any capitalization is fine

    if message.author == client.user:
        return

    if(msg == "$help"): ##prints out the commands array at the top
        await message.channel.send("You can send me any of these commands: " + str(commands))

    if (msg[1]).isdigit() & (msg[len(msg)-1]).isdigit() and (len(msg) > 3): #takes in any numer of sides with any number of sides, just needs two numbers with a d in between
        splitMsg = msg.split("d")
        numDice = int(splitMsg[0][1:])
        numSides = int(splitMsg[1])
        total = 0

        for x in range(0, numDice):
            roll = diceRoll(int(splitMsg[1]))
            addRoll(message.author, roll, numSides)
            total = total + roll
        await message.channel.send("You rolled " + str(numDice) + " d" + str(numSides) + "s for a total of " + str(total))


    if(msg == "$dicetotal"): ##prints the data stored of the users rolls
        await message.channel.send("*" + str(message.author) + "*:   **" + str(numRolls[users.index(message.author)]) + "** rolls.   Global total of **" + str(diceTotal[users.index(message.author)]) + "**.   Last rolled a d" + str(lastUsed[users.index(message.author)]))


    if(msg == "$dicegame"): ##poker like game with 4d9s
        await message.channel.send("Lets play a dice game. We'll roll 4 d9s, and you can drop one die of your choice. Best hand poker-wise wins.")
        playersHand = []
        dealersHand = []
        for x in range(0,4): ##rolling each players hand in a for loop to make sure the users rolls are kept track of
            roll = diceRoll(9)
            addRoll(message.author, roll, 9)
            playersHand.append(roll)
        for x in range(0,4):
            roll = diceRoll(9)
            dealersHand.append(roll)

        await message.channel.send("You have a hand of... " + str(playersHand) + "\n *What die do you want to reroll?*")

        channel = message.channel
        def check(m):
            return ((m.content[0].isnumeric() or (m.content.lower() == "none")) and m.channel == channel)
        newMsg = await client.wait_for('message', check=check)       ##waits for a new message in response to changing a roll

        if(newMsg.content.lower() == "none"):
            await message.channel.send("You stay with your hand of " + str(playersHand))
        elif(newMsg.content in str(playersHand)):
            newRoll = diceRoll(9)
            await message.channel.send("You switch out the " + str(newMsg.content[0]) + " and get a " + str(newRoll))
            playersHand[playersHand.index(int(newMsg.content[0]))] = newRoll
        else:
            await message.channel.send("Thats not a number you have... We'll just play later then.")
            return

        result = compareHands(playersHand, dealersHand)

        if(result):
            await message.channel.send("You end with " + str(playersHand) + " versus my hand of " + str(dealersHand) + ". Wow, you won!")
        else:
            await message.channel.send("You end with " + str(playersHand) + " versus my hand of " + str(dealersHand) + ". Loser!")
            

    #Ends chess game
    if message.content.startswith('$chess end'):
        if message.channel in chess_games:
            chess_games.pop(message.channel)
            await message.channel.send('The chess game going on in this channel has ended.')
        else:
            await message.channel.send('There was no chess game to end.')
            
    #Start of chess game
    if message.content.startswith('$chess start'):
        if message.channel in chess_games:
            await message.channel.send('A chess game in this channel is already in progress. \nUse $chess end to end the ongoing game first.')
        else:
            chess_games[message.channel] = newChess()
            newmsg = printChess(message.channel)
            await message.channel.send(' A new chess game is started.\n'+newmsg)

    #move chess piece
    if message.content.startswith('$chess move'):
        if message.channel not in chess_games:
            await message.channel.send('There is no active chess game in this channel. Use $chess start to begin a game.')
        else:
            current_move = message.content[12:]
            #Unwieldly if statement to check if move is within valid parameters of chess board
            if len(current_move) == 5 and current_move[2] == ' ' and ord(current_move[0].upper()) >= 65 and ord(current_move[0].upper()) < 73 and ord(current_move[1]) >= 49 and ord(current_move[1]) < 57 and ord(current_move[3].upper()) >= 65 and ord(current_move[3].upper()) < 73 and ord(current_move[4]) >= 48 and ord(current_move[4]) < 57:
                start_space = [8-int(current_move[1]), ord(current_move[0].upper()) - 65]
                end_space = [8-int(current_move[4]), ord(current_move[3].upper()) - 65]
                didMove = movePiece(chess_games,message.channel,start_space, end_space)
                if (didMove):
                    await message.channel.send(printChess(message.channel))
                else:
                    await message.channel.send('This move was not valid.')
            else:
                await message.channel.send('This move is invalid! Use the format $chess move [start space] [end space] (ex. $chess move G4 F4)')

    #help function for connect four
    if message.content.startswith('$c4 help'):
        await message.channel.send("""commands include:
$c4 help
$c4 reset
$c4 blu (column number)
$c4 red (column number)""")

    #Resets connect four board
    if message.content.startswith('$c4 reset'):
        global grid
        grid = [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]]
        await message.channel.send(showGrid(False))

    #Place blue piece in connect four
    if message.content.startswith('$c4 blu '):
        await message.channel.send(addPuck(int(message.content[8]) - 1, 1))

    #Place red piece in connect four
    if message.content.startswith('$c4 red '):
        await message.channel.send(addPuck(int(message.content[8]) - 1, 2))


            
client.run('') #Important - Enter bot's key as string for parameter of run function

