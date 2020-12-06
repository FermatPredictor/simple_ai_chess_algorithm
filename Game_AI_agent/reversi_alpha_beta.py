import sys
sys.path.append('..') # 添加相對路徑上兩層到sys.path，讓程式找到的模組_package
from _package._game_theory.alpha_beta_algo import MinimaxABAgent
from Basic_Game_Logic.Reversi.reversi import ReversiState

import cProfile

class AB_ReversiState(ReversiState):
    """ 
    player_color : int(usually 1 or 2, 0 for empty grid), 下一步換誰下
    """
    def __init__(self, board, playerColor):
        super().__init__(board, playerColor)
        self.eval_mode = 'weight'
        self.w_board = self.__get_weight_board()
    
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
    AI = MinimaxABAgent(7, play_color, state)
    result = AI.choose_action()
    
if __name__=='__main__':
    cProfile.run('main()')
    
    