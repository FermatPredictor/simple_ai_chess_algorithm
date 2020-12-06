from .Game_Logic_Cython.reversi_get_valid_move_cython import getValidMoves as moves

class ReversiState():
    """ 
    這邊示範如何清楚的定義一個兩人遊戲
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
        self.board = board
        self.height, self.width = len(board), len(board[0])
        self.playerColor = playerColor # int(usually 1 or 2, 0 for empty grid), 下一步換誰下
        self.pass_info = 0 # 0:無pass, 1:黑pass, 2:白pass, 3:黑白均pass，此時game over 
        
    def isOnBoard(self, r, c, H, W):
        return 0 <= r < H and 0 <= c < W
    
    def makeMove(self, action_key):
        key, pass_info = action_key
        if key != 'PASS':
            for r, c in key:
                self.board[r][c] = self.playerColor
            self.pass_info = 0
        else:
            self.pass_info = self.pass_info | self.playerColor
        self.__next_turn()
            
    def unMakeMove(self, action_key):
        key, pass_info = action_key
        self.pass_info = pass_info
        if key != 'PASS':
            _r, _c = key[0]
            self.board[_r][_c] = 0
            for r, c in key[1:]:
                self.board[r][c] = self.playerColor
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
    state = ReversiState(board, play_color)
    print(state.getValidMoves())

    
if __name__=='__main__':
    main()
    
    