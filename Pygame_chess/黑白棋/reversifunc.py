import random
import globalvar as gv

import sys
sys.path.append('../..') # 添加相對路徑上兩層到sys.path，讓程式找到的模組_package
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
    
    def next_turn(self):
        self.playerColor = self.opp_color()

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
        self.eval_mode = 'weight'
    
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
        state.next_turn()
            
    def unMakeMove(self, state, action_key):
        place_x, place_y = action_key[0]
        state.board[place_x][place_y] = 0
        for x, y in action_key[1:]:
            state.board[x][y] = state.playerColor
        state.next_turn()


    def getValidMoves(self, state):
        moves = {(x, y):self.isValidMove(state, x,y) for x in range(self.width) for y in range(self.height)}
        return {k:v for k,v in moves.items() if v}
    
        
    def evaluation_function(self, state, tile):
        score, opp = 0, 3^tile
        for x in range(8):
            for y in range(8):
                if state.board[x][y] == tile:
                    score += weights[x][y] if self.eval_mode == 'weight' else 1
                elif state.board[x][y] == opp:
                    score -= weights[x][y] if self.eval_mode == 'weight' else 1
        return score
        
    
    def is_terminal(self, state):
        terminal = False
        if not self.getValidMoves(state):
            state.next_turn()
            if not self.getValidMoves(state):
                terminal = True
            state.next_turn()
        return terminal
    

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
    
    def check_move(self):
        # 輪空規則
        valid_moves = self.game.getValidMoves(self.state)
        if not valid_moves:
            self.state.next_turn()
            
    def change_turn(self):
        self.state.next_turn()
            
    def set_board(self, x, y):
        self.state.board[x][y] = (self.state.board[x][y]+1)%3
            
    def get_board(self):
        return self.state.board
    
    def get_turn(self):
        return self.state.playerColor
    
    def get_hint(self):
        return set(self.game.getValidMoves(self.state))
    
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
    
    def __count_empty_grid(self):
        empty_grid = 0
        for x in range(self.width):
            for y in range(self.height):
                if self.state.board[y][x]==0:
                    empty_grid += 1
        return empty_grid
    
    def ai_action(self):
        end_mode = self.__count_empty_grid()<=12
        self.game.eval_mode = 'weight' if not end_mode else 'num'
        depth = 5 if not end_mode else 10
        if end_mode:
            print('end mode analysize...')
        AI = MinimaxABAgent(depth, self.get_turn(), self.game, self.state)
        AI.choose_action()
