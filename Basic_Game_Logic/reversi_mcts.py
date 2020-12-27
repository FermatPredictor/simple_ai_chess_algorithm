import sys
sys.path.append('..') # 添加相對路徑上兩層到sys.path，讓程式找到的模組_package
from _package._game_theory.mcts_algo import MonteCarloTreeSearch, MonteCarloTreeSearchNode, parallel_MCTS

from array import array
import cProfile

if __name__=='__main__':
    from Fast_Reversi_Cython.reversi_cython import getValidMoves as moves
    from Fast_Reversi_Cython.reversi_cython import count_tile
else:
    from Fast_Reversi_Cython.reversi_cython import getValidMoves as moves
    from Fast_Reversi_Cython.reversi_cython import count_tile

class MCTS_ReversiState():

    def __init__(self, board, playerColor):
        self.board = array('i', sum(board,[]))
        self.height, self.width = len(board), len(board[0])
        self.playerColor = playerColor # int(usually 1 or 2, 0 for empty grid), 下一步換誰下
        self.pass_info = 0 # 0:無pass, 1:黑pass, 2:白pass, 3:黑白均pass，此時game over
        self.eval_mode = 'weight'
        
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

def mcts_action(board, playerColor):
    state = MCTS_ReversiState(board, playerColor)
    AI = MonteCarloTreeSearch(MonteCarloTreeSearchNode(state))
    result = AI.best_action(1000)
    return result.action[0]


def parallel_mcts_action(board, playerColor):
    state = MCTS_ReversiState(board, playerColor)
    AI = parallel_MCTS(MonteCarloTreeSearchNode(state))
    result = AI.best_action(1000)
    return result.action[0]


def main():
    playerColor = 1
#    board = [[0,2,1,2,0,0,0,0],
#               [0,0,0,0,0,0,0,0],
#               [0,0,0,0,0,0,0,0],
#               [0,0,0,0,0,0,0,0],
#               [0,0,0,0,0,0,0,0],
#               [0,0,0,0,0,0,0,0],
#               [0,0,0,0,0,0,0,0],
#               [0,0,0,0,0,0,0,0]]
    board = [[0,0,0,0,0,0,0,0],
              [0,0,0,0,0,0,0,0],
              [0,0,0,1,0,0,0,0],
              [0,0,2,2,2,2,0,0],
              [0,0,0,1,2,0,0,0],
              [0,0,0,0,0,0,0,0],
              [0,0,0,0,0,0,0,0],
              [0,0,0,0,0,0,0,0]]

#    board = [[2,2,2,2,2,2,2,2],
#             [1,1,1,1,2,1,2,2],
#             [1,1,2,2,2,2,1,2],
#             [0,1,1,2,2,1,2,2],
#             [0,1,1,2,1,2,2,2],
#             [1,1,2,2,2,2,2,2],
#             [1,1,1,1,1,2,0,2],
#             [2,2,2,2,2,2,0,0]]
    #mcts_action(board, playerColor)
    parallel_mcts_action(board, playerColor)

    
    
if __name__=='__main__':
    #cProfile.run('main()')
    main()
    
    