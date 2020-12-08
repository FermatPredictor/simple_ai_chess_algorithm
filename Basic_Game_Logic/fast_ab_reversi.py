import sys
sys.path.append('..') # 添加相對路徑上兩層到sys.path，讓程式找到的模組_package
from _package._game_theory.alpha_beta_algo import MinimaxABAgent

from array import array
import cProfile

if __name__=='__main__':
    from Fast_Reversi_Cython.reversi_cython import getValidMoves as moves
    from Fast_Reversi_Cython.reversi_python import eval_func as ef
    from Fast_Reversi_Cython.reversi_python import count_tile
else:
    from .Fast_Reversi_Cython.reversi_cython import getValidMoves as moves
    from .Fast_Reversi_Cython.reversi_cython import eval_func as ef
    from .Fast_Reversi_Cython.reversi_cython import count_tile

class AB_ReversiState():
    """ 
    - playerColor:  int(usually 1 or 2, 0 for empty grid), 下一步換誰下
    - getValidMoves(self): 下一步有哪些合法棋步可走，回傳字典:{合法棋步座標: 翻轉的對手棋子}，
                           通常是各ai算法的核心，很值得優化速度
    - makeMove(self, action_key): 根據action_key走棋 
    - unMakeMove(self, action_key): 根據同一個action_key還原棋步，通常用於alpha_beta算法避免創建過多state
    - is_terminal(self): 判斷遊戲是否結束了
    - winner(self): 遊戲結束的狀況下，判斷贏家是誰(0 for 和棋)
    - next_turn(self): 若遇到輪空的狀況，換下一個玩家行動
    """
    def __init__(self, board, playerColor):
        self.board = array('i', sum(board,[]))
        self.height, self.width = len(board), len(board[0])
        self.playerColor = playerColor # int(usually 1 or 2, 0 for empty grid), 下一步換誰下
        self.pass_info = 0 # 0:無pass, 1:黑pass, 2:白pass, 3:黑白均pass，此時game over
        self.eval_mode = 'weight'
        self.w_board = array('i', sum(self.__get_weight_board(), []))
        
    def isOnBoard(self, r, c, H, W):
        return 0 <= r < H and 0 <= c < W
    
    def makeMove(self, action_key):
        key, pass_info = action_key
        if key != 'PASS':
            for idx in key:
                self.board[idx] = self.playerColor
            self.pass_info = 0
        else:
            self.pass_info |= self.playerColor
        self.__next_turn()
            
    def unMakeMove(self, action_key):
        key, pass_info = action_key
        self.pass_info = pass_info
        if key != 'PASS':
            self.board[key[0]] = 0
            for idx in key[1:]:
                self.board[idx] = self.playerColor
        self.__next_turn()
    
    def getValidMoves(self):
        return moves(self.board, self.height, self.width, self.playerColor, self.pass_info)
                
    def __opp_color(self):
        return 3^self.playerColor
    
    def __next_turn(self):
        self.playerColor = self.__opp_color()
        
    def winner(self):
        score = {0:0, 1:0, 2:0}
        for r in range(self.height):
            for c in range(self.width):
                score[self.board[r][c]] += 1
        if score[1]>score[2]:
            return 1
        if score[1]<score[2]:
            return 2
        return 0  
    
    def is_terminal(self):
        return self.pass_info == 3
    
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
        return ef(self.board, self.height, self.width, tile, self.w_board) if self.eval_mode == 'weight' \
               else count_tile(self.board, self.height, self.width, tile)
    
def test_getValidMoves():
    """ 測試找合法棋步 """
    play_color = 1
    board = [[0,0,0,0,0,0,0,0],
              [0,0,0,0,0,0,0,0],
              [0,0,0,1,0,0,0,0],
              [0,0,2,2,2,2,0,0],
              [0,0,0,1,2,0,0,0],
              [0,0,0,0,0,0,0,0],
              [0,0,0,0,0,0,0,0],
              [0,0,0,0,0,0,0,0]]
    state = AB_ReversiState(board, play_color)
    print(state.getValidMoves())
    
def test_eval_func():
    """ 測試找合法棋步 """
    play_color = 1
    board = [[0,0,0,0,0,0,0,0],
              [0,0,0,0,0,0,0,0],
              [0,0,0,1,0,0,0,0],
              [0,0,2,2,2,2,0,0],
              [0,0,0,1,2,0,0,0],
              [0,0,0,0,0,0,0,0],
              [0,0,0,0,0,0,0,0],
              [0,0,0,0,0,0,0,0]]
    state = AB_ReversiState(board, play_color)
    print(state.evaluation_function(play_color))

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
    
    # play_color = 2
    # board = [[2,2,2,2,2,2,2,2],
    #          [1,1,1,1,2,1,2,2],
    #          [1,1,2,2,2,2,1,2],
    #          [0,1,1,2,2,1,2,2],
    #          [0,1,1,2,1,2,2,2],
    #          [1,1,2,2,2,2,2,2],
    #          [1,1,1,1,1,2,0,2],
    #          [2,2,2,2,2,2,0,0]]
    
    # play_color = 1
    # board =[[0, 2, 2, 2, 0, 1, 2, 2],
    #          [0, 1, 1, 1, 1, 2, 2, 2],
    #          [0, 0, 1, 2, 2, 2, 2, 2],
    #          [0, 1, 1, 1, 2, 2, 2, 0],
    #          [2, 1, 1, 2, 1, 1, 2, 0],
    #          [2, 2, 1, 2, 2, 1, 2, 2],
    #          [2, 2, 1, 1, 2, 2, 1, 0],
    #          [0, 2, 2, 2, 2, 2, 0, 0]]

    state = AB_ReversiState(board, play_color)
    #print(state.getValidMoves())
    AI = MinimaxABAgent(8, play_color, state)
    result = AI.choose_action()
    
if __name__=='__main__':
    #test_getValidMoves()
    #test_eval_func()
    cProfile.run('main()')
    
    