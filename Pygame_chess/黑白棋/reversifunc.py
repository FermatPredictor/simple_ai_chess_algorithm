import random
import globalvar as gv

# 寫黑白棋遊戲的基本邏輯，棋子共'X','O'兩種
class Reversi():
    def __init__(self, height, width):
        self.width = width
        self.height = height
        self.board = [[' ']*self.height for i in range(self.width)]
    
    # 初始化棋盤
    def iniBoard(self):
        for i in range(self.width):
            for j in range(self.height):
                self.board[i][j]=' '
        W, H = self.width//2 , self.height//2
        self.board[W-1][H-1]='X'
        self.board[W-1][H]='O'
        self.board[W][H-1]='O'
        self.board[W][H]='X'
    
    def isOnBoard(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

    #檢查tile放在某個座標是否為合法棋步，如果是則回傳被翻轉的棋子
    def isValidMove(self, tile, xstart, ystart):
        if not self.isOnBoard(xstart, ystart) or self.board[xstart][ystart]!=' ':
            return []
        self.board[xstart][ystart] = tile # 暫時放置棋子
        otherTile = 'O'  if tile == 'X' else 'X'
        tilesToFlip = [] # 合法棋步
        dirs = [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]] # 定義八個方向
        for xdir, ydir in dirs:
            x, y = xstart+xdir, ystart+ydir
            while self.isOnBoard(x, y) and self.board[x][y] == otherTile:
                x += xdir
                y += ydir
                # 夾到對手的棋子了，回頭記錄被翻轉的對手棋子
                if self.isOnBoard(x, y) and self.board[x][y] == tile:
                    while True:
                        x -= xdir
                        y -= ydir
                        if x == xstart and y == ystart:
                            break
                        tilesToFlip.append([x, y])
                        
        self.board[xstart][ystart] = ' ' # 重設為空白
        return tilesToFlip

    # 若將tile放在xstart, ystart是合法行動，放置棋子
    # 回傳被翻轉的棋子(用來電腦算棋時可以把棋子翻回來)
    def makeMove(self, tile, xstart, ystart):
        tilesToFlip = self.isValidMove(tile, xstart, ystart)
        if tilesToFlip:
            self.board[xstart][ystart] = tile
            for x, y in tilesToFlip:
                self.board[x][y] = tile
        return tilesToFlip

    # 回傳現在盤面輪到tile走的所有合法棋步
    def getValidMoves(self, tile):
        return [[x, y] for x in range(self.width) for y in range(self.height) if self.isValidMove(tile, x, y)]
    
    # 計算當前比分
    def getScoreOfBoard(self)-> dict:
        scores = {'X':0, 'O':0}
        for x in range(self.width):
            for y in range(self.height):
                tile = self.board[x][y]
                if tile in scores:
                    scores[tile] += 1
        return scores
    
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


