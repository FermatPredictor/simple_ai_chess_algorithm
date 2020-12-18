import sys
sys.path.append('..') # 添加相對路徑上兩層到sys.path，讓程式找到的模組_package
from _package._game_theory.alpha_beta_algo import MinimaxABAgent

from array import array
import cProfile

if __name__=='__main__':
    from Fast_Reversi_Cython.reversi_cython import getValidMoves as moves
    from Fast_Reversi_Cython.reversi_cython import eval_func as ef
    from Fast_Reversi_Cython.reversi_cython import count_tile
else:
    from .Fast_Reversi_Cython.reversi_cython import getValidMoves as moves
    from .Fast_Reversi_Cython.reversi_cython import eval_func as ef
    from .Fast_Reversi_Cython.reversi_cython import count_tile

class AB_ReversiState():
    """ 
    優化歷程概要:
    目前這個版本跟一開始的版本相比，
    大約從每秒搜索1萬個節點提速至20萬個節點，可謂竭盡所能之究極加速
    <遊戲邏輯>
    1. 搜索合法步: 原搜索所有空格，改為由自己棋子出發搜索更佳
    2. 判斷終局: 原判斷黑白雙方都無合法棋步，現記錄上一手誰pass，改判雙方都pass後結束
    <棋盤結構選擇>
    目前用array模組的array，用於陣列元素都是同一種類別，為一維結構，比二維快，也比list快
    為何不用numpy?
    numpy的特長是數學計算快，但是單純的陣列存取元素反而更慢。
    class內計算採用array，然而對外接口為方便實作(比如說ui畫圖)，
    對外接口的input, output仍用二維list
    <Cython>
    類python語言，透過事前指定每個變數的型別，提速十分明顯
    
    【測速須知】
    目前用cProfile分析各函數調用的時間，
    注意「觀測」本身會讓程式變慢，
    故作用是找出程式相對慢的部分再抓出來加速。
    
    【加速還有哪些突破口?】
    平行化: 榨乾CPU資源
    ab算法: 若棋步有好的排序，剪枝效果會更明顯
    
    【class 函數簡介】    
    - playerColor:  int(usually 1 or 2, 0 for empty grid), 下一步換誰下
    - getValidMoves(self): 下一步有哪些合法棋步可走，回傳字典:{合法棋步座標: 翻轉的對手棋子}，
                           通常是各ai算法的核心，很值得優化速度
    - makeMove(self, action_key): 根據action_key走棋 
    - unMakeMove(self, action_key): 根據同一個action_key還原棋步，通常用於alpha_beta算法避免創建過多state
    - is_terminal(self): 判斷遊戲是否結束了
    - winner(self, tile): 遊戲結束的狀況下，判斷贏家是誰(0 for 和棋)
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
        self.playerColor ^=3
            
    def unMakeMove(self, action_key):
        key, pass_info = action_key
        self.pass_info = pass_info
        if key != 'PASS':
            self.board[key[0]] = 0
            for idx in key[1:]:
                self.board[idx] = self.playerColor
        self.playerColor ^=3
    
    def getValidMoves(self):
        return moves(self.board, self.height, self.width, self.playerColor, self.pass_info)
                
        
    def winner(self, tile):
        score = count_tile(self.board, tile)
        if score>0:
            return 1
        if score<0:
            return -1
        return 0   
    
    def is_terminal(self):
        return self.pass_info == 3
    
    def to_board(self):
        L = self.board
        step = self.width
        return [list(L[r:r+step]) for r in range(0,len(L),step)]
    
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
        return ef(self.board, tile, self.w_board) if self.eval_mode == 'weight' else count_tile(self.board, tile)
    
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
    #cProfile.run('main()')
    main()
    
    