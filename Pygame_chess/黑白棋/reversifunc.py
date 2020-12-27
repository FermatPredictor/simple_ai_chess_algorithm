import sys
sys.path.append('../..') # 添加相對路徑上兩層到sys.path，讓程式找到的模組_package
from Basic_Game_Logic.reversi_fast_ab import AB_ReversiState
from _package.game_engine.general_game_engine import Game_Engine
from Basic_Game_Logic.reversi_fast_ab import ab_action
from Basic_Game_Logic.reversi_mcts import mcts_action, parallel_mcts_action

class Reversi_Game(Game_Engine):
    
    def __init__(self, state, black_ai, white_ai):
        super().__init__(state, black_ai, white_ai)
        
    def set_board(self, x, y):
        idx = x*self.state.width+y
        self.state.board[idx] = (self.state.board[idx]+1)%3
        
    # 計算當前比分
    def getScoreOfBoard(self)-> dict:
        scores = {1:0, 2:0}
        for tile in self.state.board:
            if tile in scores:
                scores[tile] += 1
        return scores[1], scores[2]
    

def reversi_init_game(height, width, black_ai=ab_action, white_ai=ab_action):
    board = [[0]*width for _ in range(height)]
    H, W = height//2, width//2
    board[H-1][W-1], board[H-1][W] = 2, 1
    board[H][W-1], board[H][W] = 1, 2
    state = AB_ReversiState(board, 1)
    return Reversi_Game(state, black_ai, white_ai)
