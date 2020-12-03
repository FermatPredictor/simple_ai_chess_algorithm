import sys
sys.path.append('..') # 添加相對路徑上兩層到sys.path，讓程式找到的模組_package
from _package._game_theory.alpha_beta_algo import MinimaxABAgent

import cProfile

class ReversiState():
    """ 
    player_color : int(usually 1 or 2, 0 for empty grid), 下一步換誰下
    """
    def __init__(self, board, playerColor):
        self.board = board
        self.height, self.width = len(board), len(board[0])
        self.playerColor = playerColor
        self.eval_mode = 'weight'
        self.pass_info = 0 # 0:無pass, 1:黑pass, 2:白pass, 3:黑白均pass，此時game over 
        self.w_board = self.__get_weight_board()
        
    def isOnBoard(self, r, c, H, W):
        return 0 <= r < H and 0 <= c < W
    
    #檢查tile放在某個座標是否為合法棋步，如果是則回傳翻轉的對手棋子
    def isValidMove(self, r, c):
        if self.board[r][c]!=0:
            return False
        tile, opp_tile = self.playerColor , self.opp_color()
        tilesToFlip = []
        dirs = [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]] # 定義八個方向
        for dr, dc in dirs:
            _r, _c, flip = r+dr, c+dc, 0
            while self.isOnBoard(_r, _c, self.height,self.width) and self.board[_r][_c] == opp_tile:
                tilesToFlip.append([_r, _c])
                _r, _c, flip = _r+dr, _c+dc, flip+1
            if flip and not(self.isOnBoard(_r, _c, self.height,self.width) and self.board[_r][_c] == tile):
               tilesToFlip = tilesToFlip[:-flip] # 沒夾到對手的棋子，抹去記錄
        if tilesToFlip:
            return [[r, c]] + tilesToFlip
        return False
    
    def makeMove(self, action_key):
        key, pass_info = action_key
        if key != 'PASS':
            for r, c in key:
                self.board[r][c] = self.playerColor
            self.pass_info = 0
        else:
            self.pass_info = self.pass_info | self.playerColor
        self.next_turn()
            
    def unMakeMove(self, action_key):
        key, pass_info = action_key
        self.pass_info = pass_info
        if key != 'PASS':
            _r, _c = key[0]
            self.board[_r][_c] = 0
            for r, c in key[1:]:
                self.board[r][c] = self.playerColor
        self.next_turn()

    def getValidMoves(self):
        """
        TODO: 目前做時間優化，暫將ai的「random」close，
        As is: 檢查棋盤上的所有格子
        To be: 先定位對手棋子，每次看上下、左右、兩斜角，
        若兩方向一空一邊有棋子，那個空格才有可能是合法棋步
        """
        moves = {(x, y):self.isValidMove(x,y) for x in range(self.height) for y in range(self.width)}
        move_fliter = {k:(v, self.pass_info) for k,v in moves.items() if v}
        return move_fliter if move_fliter else {'PASS': ('PASS', self.pass_info)}
    
    def opp_color(self):
        return 3^self.playerColor
    
    def next_turn(self):
        self.playerColor = self.opp_color()
    
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
        
    def evaluation_function(self, tile):
        score, opp = 0, tile^3
        coef = {0:0, tile: 1, opp:-1} 
        for r in range(self.height):
            for c in range(self.width):
                score += (self.w_board[r][c] if self.eval_mode == 'weight' else 1)* coef[self.board[r][c]]
        return score
        
    
    def is_terminal(self):
        return self.pass_info == 3

def main():
    """
    黑白棋套用alpha-beta算法
    平均每秒可搜索10000個節點以上
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
    """
    board = [[2,2,2,2,2,2,2,2],
             [1,1,1,1,2,1,2,2],
             [1,1,2,2,2,2,1,2],
             [0,1,1,2,2,1,2,2],
             [0,1,1,2,1,2,2,2],
             [1,1,2,2,2,2,2,2],
             [1,1,1,1,1,2,0,2],
             [2,2,2,2,2,2,0,0]]
    """
    state = ReversiState(board, play_color)
    AI = MinimaxABAgent(7, play_color, state)
    result = AI.choose_action()
    
if __name__=='__main__':
    cProfile.run('main()')
    
    