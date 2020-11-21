import sys
sys.path.append('..') # 添加相對路徑上兩層到sys.path，讓程式找到的模組_package
from _package._game_theory.alpha_beta_algo import MinimaxABAgent

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
    
if __name__=='__main__':
    """
    黑白棋套用alpha-beta算法
    通過 https://www.hackerrank.com/challenges/reversi/problem 的測試
    平均每秒搜索6000個節點，效能可能有待改善
    """
    play_color = 1
    board = [[0,0,0,0,0,0,0,0],
             [0,0,0,0,0,0,0,0],
             [0,0,0,1,0,0,0,0],
             [0,0,2,2,2,2,0,0],
             [0,0,0,1,2,0,0,0],
             [0,0,0,0,0,0,0,0],
             [0,0,0,0,0,0,0,0],
             [0,0,0,0,0,0,0,0]]
    state = State(board, play_color)
    game = Reversi(8,8)
    AI = MinimaxABAgent(7, play_color, game, state)
    result = AI.choose_action()