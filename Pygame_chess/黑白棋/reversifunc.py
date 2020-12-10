import sys
sys.path.append('../..') # 添加相對路徑上兩層到sys.path，讓程式找到的模組_package
from _package._game_theory.alpha_beta_algo import MinimaxABAgent
#from Game_AI_agent.reversi_alpha_beta import AB_ReversiState
from Basic_Game_Logic.fast_ab_reversi import AB_ReversiState
    

class Reversi_Game():
    def __init__(self, height, width):
        self.height, self.width = height, width
        board = [[0]*width for _ in range(height)]
        H, W = height//2, width//2
        board[H-1][W-1], board[H-1][W] = 2, 1
        board[H][W-1], board[H][W] = 1, 2
        self.state = AB_ReversiState(board, 1)
        
    def make_move(self, x, y):
        valid_moves = self.state.getValidMoves()
        if (x,y) in valid_moves:
            self.state.makeMove(valid_moves[(x,y)])
    
    def check_move(self):
        # 輪空規則
        valid_moves = self.get_hint()
        if not valid_moves:
            self.change_turn()
            
    def change_turn(self):
        self.state.makeMove(('PASS', 0))
            
    def set_board(self, x, y):
        idx = x*self.width+y
        self.state.board[idx] = (self.state.board[idx]+1)%3
            
    def get_board(self):
        return self.state.to_board()
    
    def get_turn(self):
        return self.state.playerColor
    
    def get_hint(self):
        return set(self.state.getValidMoves()) - {'PASS'}
    
    def is_terminal(self):
        return self.state.is_terminal()
    
    # 計算當前比分
    def getScoreOfBoard(self)-> dict:
        scores = {1:0, 2:0}
        for x in range(self.height):
            for y in range(self.width):
                tile = self.get_board()[x][y]
                if tile in scores:
                    scores[tile] += 1
        return scores[1], scores[2]
    
    def __count_empty_grid(self):
        empty_grid = 0
        for x in range(self.height):
            for y in range(self.width):
                if self.get_board()[x][y]==0:
                    empty_grid += 1
        return empty_grid
    
    def ai_action(self):
        end_mode = self.__count_empty_grid()<=14
        self.state.eval_mode = 'weight' if not end_mode else 'num'
        depth = 6 if not end_mode else 10
        if end_mode:
            print('end mode analysize...')
        AI = MinimaxABAgent(depth, self.get_turn(), self.state)
        AI.choose_action()


