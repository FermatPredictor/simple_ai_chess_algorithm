import random
import globalvar as gv
from aifunc import MinimaxABAgent

class State():
    """ 
    記錄棋盤資訊，及下一步換誰下
    player_color : int(usually 1 or 2, 0 for empty grid)
    """
    def __init__(self, board, playerColor):
        self.board = board
        self.playerColor = playerColor
    
    def opp_color(self):
        return 3^self.playerColor

# the weights of board, big positive value means top priority for opponent
weights = [[ 100, -20,  10,   5,   5,  10, -20, 100],
           [ -20, -50,  -2,  -2,  -2,  -2, -50, -20],
           [  10,  -2,   1,   1,   1,   1,  -2,  10],
           [   5,  -2,   1,   1,   1,   1,  -2,   5],
           [   5,  -2,   1,   1,   1,   1,  -2,   5],
           [  10,  -2,   1,   1,   1,   1,  -2,  10],
           [ -20, -50,  -2,  -2,  -2,  -2, -50, -20],
           [ 100, -20,  10,   5,   5,  10, -20, 100]]


class Reversi():
    def __init__(self, height, width):
        self.width = width
        self.height = height
    
    def isOnBoard(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

    #檢查tile放在某個座標是否為合法棋步，如果是則回傳翻轉的對手棋子
    def isValidMove(self, state, xstart, ystart):
        if not self.isOnBoard(xstart, ystart) or state.board[xstart][ystart]!=0:
            return False
        tile, opp_tile = state.playerColor , state.opp_color()
        tilesToFlip = []
        dirs = [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]] # 定義八個方向
        for xdir, ydir in dirs:
            x, y = xstart+xdir, ystart+ydir
            while self.isOnBoard(x, y) and state.board[x][y] == opp_tile:
                x, y = x+xdir, y+ydir
                # 夾到對手的棋子了，回頭記錄被翻轉的對手棋子
                if self.isOnBoard(x, y) and state.board[x][y] == tile:
                    x, y = x-xdir, y-ydir
                    while not (x == xstart and y == ystart):
                        tilesToFlip.append([x, y])
                        x, y = x-xdir, y-ydir
        if tilesToFlip:
            return [[xstart, ystart]] + tilesToFlip
        return False


    def makeMove(self, state, action_key):
        for x, y in action_key:
            state.board[x][y] = state.playerColor
        state.playerColor = state.opp_color()
            
    def unMakeMove(self, state, action_key):
        place_x, place_y = action_key[0]
        state.board[place_x][place_y] = 0
        for x, y in action_key[1:]:
            state.board[x][y] = state.playerColor
        state.playerColor = state.opp_color()


    def getValidMoves(self, state):
        moves = {(x, y):self.isValidMove(state, x,y) for x in range(self.width) for y in range(self.height)}
        return {k:v for k,v in moves.items() if v}
    
    def evaluation_function(self, state, tile):
        # for 8*8 的計分
        score = 0
        opp = 3-tile
        for x in range(8):
            for y in range(8):
                if state.board[x][y] == tile:
                    score += weights[x][y]
                elif state.board[x][y] == opp:
                    score -= weights[x][y]    
        return score
    
    def is_terminal(self, state):
        if not self.getValidMoves(state):
            state.playerColor = state.opp_color()
            if not self.getValidMoves(state):
                state.playerColor = state.opp_color()
                return True
            state.playerColor = state.opp_color()
        return False
    

class Reversi_Gmae():
    def __init__(self):
        self.game = Reversi(8,8)
        self.width, self.height = 8,8
        board = [[0]*8 for _ in range(8)]
        board[3][3], board[3][4] = 2, 1
        board[4][3], board[4][4] = 1, 2
        self.state = State(board, 1)
        
    def make_move(self, x, y):
        valid_moves = self.game.getValidMoves(self.state)
        if (x,y) in valid_moves:
            self.game.makeMove(self.state, valid_moves[(x,y)])
            
    def get_board(self):
        return self.state.board
    
    def get_turn(self):
        return self.state.playerColor
    
    def is_terminal(self):
        return self.game.is_terminal(self.state)
    
    # 計算當前比分
    def getScoreOfBoard(self)-> dict:
        scores = {1:0, 2:0}
        for x in range(self.width):
            for y in range(self.height):
                tile = self.state.board[y][x]
                if tile in scores:
                    scores[tile] += 1
        return scores[1], scores[2]
    
    def ai_action(self):
        AI = MinimaxABAgent(3, self.get_turn(), self.game, self.state)
        AI.choose_action()
        

# initialize the board to starting position
def initializeBoard(board):
    board[3][3], board[3][4] = gv.P2, gv.P1
    board[4][3], board[4][4] = gv.P1, gv.P2
    return board

# shows the board, used for debugging purposes
def showBoard(board):
    for x in range(8):
        for y in range(8):
            print(board[x][y], end=' ')
        print('')

# checks if the value assigned are within the index of the board
def isOnBoard(x, y):
    return (0<=x<=7) and (0<=y<=7)

# get the amount of empty tiles available in a board
def getEmptyTiles(board):
    empty = 0

    for x in range(8):
        for y in range(8):
            if board[x][y] == '.':
                empty += 1

    return empty

# returns opponent's pieces that can be flipped when a player place their piece in a selected position
def getDisksToFlip(board, turn, x_pos, y_pos):
    if board[x_pos][y_pos] != '.' or not isOnBoard(x_pos, y_pos):
        return []

    if (turn == gv.P1):
        enemy = gv.P2
    elif (turn == gv.P2):
        enemy = gv.P1

    validDisks = []

    for x_move, y_move in [[-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 1], [1, -1], [1, 0], [1, 1]]:
        x_cur, y_cur = x_pos, y_pos
        x_cur += x_move
        y_cur += y_move

        # check if the current tile is enemy's and in within the board
        if isOnBoard(x_cur, y_cur) and board[x_cur][y_cur] == enemy:
            x_cur += x_move
            y_cur += y_move

            # go back to for if the tile's coordinate is not in the board
            if not isOnBoard(x_cur, y_cur):
                continue

            # check if there is more enemy on the current move, done if
            while board[x_cur][y_cur] == enemy:
                x_cur += x_move
                y_cur += y_move

                if not isOnBoard(x_cur, y_cur):
                    break

            if not isOnBoard(x_cur, y_cur):
                continue

            if board[x_cur][y_cur] == turn:
                while True:
                    x_cur -= x_move
                    y_cur -= y_move

                    if x_cur == x_pos and y_cur == y_pos:
                        break

                    validDisks.append([x_cur, y_cur])

    return validDisks

# get the valid moves in coordinates of a board
def getValidMoves(board, turn):
    validMoves = []

    for x in range(8):
        for y in range(8):
            if getDisksToFlip(board, turn, x, y) != []:
                validMoves.append([x, y])

    return validMoves

# modify the board after a disk is placed on it
def makeMove(board, turn, x_pos, y_pos):
    tilesToFlip = getDisksToFlip(board, turn, x_pos, y_pos)

    if len(tilesToFlip) != 0:
        board[x_pos][y_pos] = turn
        for x_cur, y_cur in tilesToFlip:
            board[x_cur][y_cur] = turn

    return board

# get the score of the pieces in a board
def getScore(board):
    b_score, w_score = 0, 0

    for x in range(8):
        for y in range(8):
            if board[x][y] == gv.P1:
                b_score += 1
            elif board[x][y] == gv.P2:
                w_score += 1

    return b_score, w_score


