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


class Reversi():
    def __init__(self, height, width):
        self.width = width
        self.height = height
        self.eval_mode = 'weight'
    
    def isOnBoard(self, x, y):
        return 0 <= x < self.height and 0 <= y < self.width

    #檢查tile放在某個座標是否為合法棋步，如果是則回傳翻轉的對手棋子
    def isValidMove(self, state, xstart, ystart):
        if not self.isOnBoard(xstart, ystart) or state.board[xstart][ystart]!=0:
            return False
        tile, opp_tile = state.playerColor , state.opp_color()
        tilesToFlip = []
        dirs = [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]] # 定義八個方向
        for xdir, ydir in dirs:
            x, y, flips = xstart+xdir, ystart+ydir, 0
            while self.isOnBoard(x, y) and state.board[x][y] == opp_tile:
                tilesToFlip.append([x,y])
                x, y, flips = x+xdir, y+ydir, flips+1
            if flips>0 and not(self.isOnBoard(x, y) and state.board[x][y] == tile):
                tilesToFlip = tilesToFlip[:-flips] # 沒夾到對手的棋子，抹去記錄
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
        moves = {(x, y):self.isValidMove(state, x,y) for x in range(self.height) for y in range(self.width)}
        return {k:v for k,v in moves.items() if v}
    
    def __spiral_coords(self, board, r1, c1, r2, c2, weights):
        """
        遍歷矩陣之外圈，
        並將角、C位、邊設權重
        """
        def Pos(r,c):
            if r in [r1+1, r2-1] or c in [c1+1,c2-1]:
                return 1
            return 2
                
        for c in range(c1, c2 + 1):
            board[r1][c] = weights[Pos(r1,c)]
        for r in range(r1 + 1, r2 + 1):
            board[r][c2] = weights[Pos(r,c2)]
        for c in range(c2 - 1, c1, -1):
            board[r2][c] = weights[Pos(r2,c)]
        for r in range(r2, r1, -1):
            board[r][c1] = weights[Pos(r,c1)]
        board[r1][c1], board[r1][c2], board[r2][c1], board[r2][c2] = [weights[0]]*4
    
    def __get_weight_board(self):
        """
        這邊手動調整格子對應的權重分配，
        對應「角、C位、邊、星位、中央邊、中央」
        """
        if self.width<6 and self.height<6:
            # 棋盤過小，直接數棋子數
            return [[1]*self.width for _ in range(self.height)]
            
        weights = [100,-10,20,-50,-2, 1]
        w_board = [[weights[5]]*self.width for _ in range(self.height)]
        self.__spiral_coords(w_board, 0,0,self.height-1, self.width-1, weights[:3])
        self.__spiral_coords(w_board, 1,1,self.height-2, self.width-2, weights[3:5]+[weights[4]])
        return w_board
        
    def evaluation_function(self, state, tile):
        score, opp = 0, 3^tile
        w_board = self.__get_weight_board()
        for x in range(self.height):
            for y in range(self.width):
                if state.board[x][y] == tile:
                    score += w_board[x][y] if self.eval_mode == 'weight' else 1
                elif state.board[x][y] == opp:
                    score -= w_board[x][y] if self.eval_mode == 'weight' else 1
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
    def __init__(self, height, width):
        self.game = Reversi(height, width)
        self.height, self.width = height, width
        board = [[0]*width for _ in range(height)]
        H, W = height//2, width//2
        board[H-1][W-1], board[H-1][W] = 2, 1
        board[H][W-1], board[H][W] = 1, 2
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
        for x in range(self.height):
            for y in range(self.width):
                tile = self.state.board[x][y]
                if tile in scores:
                    scores[tile] += 1
        return scores[1], scores[2]
    
    def __count_empty_grid(self):
        empty_grid = 0
        for x in range(self.height):
            for y in range(self.width):
                if self.state.board[x][y]==0:
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
