import sys
sys.path.append('..') # 添加相對路徑上兩層到sys.path，讓程式找到的模組_package

from Basic_Game_Logic.reversi_fast_ab import AB_ReversiState
from Basic_Game_Logic.reversi_fast_ab import ab_action
from Basic_Game_Logic.reversi_mcts import mcts_action

class Reversi_Game():
    def __init__(self, height, width):
        self.height, self.width = height, width
        board = [[0]*width for _ in range(height)]
        H, W = height//2, width//2
        board[H-1][W-1], board[H-1][W] = 2, 1
        board[H][W-1], board[H][W] = 1, 2
        self.state = AB_ReversiState(board, 1)
        
    def make_move(self, r,c):
        valid_moves = self.state.getValidMoves()
        if (r,c) in valid_moves:
            self.state.makeMove(valid_moves[(r,c)])
        else:
            raise Exception('The move is not valid.')
            
    def change_turn(self):
        self.state.makeMove(('PASS', 0))

        
    def check_move(self):
        # 輪空規則
        valid_moves = self.get_hint()
        if not valid_moves:
            self.change_turn()
        
    def get_hint(self):
        return set(self.state.getValidMoves()) - {'PASS'}
    
    def get_turn(self):
        return self.state.playerColor
    
    def get_board(self):
        return self.state.to_board()
    
    def is_terminal(self):
        return self.state.is_terminal()
        
    def blackAI(self, board):
        return mcts_action(board, 1)
    
    def whiteAI(self, board):
        return ab_action(board, 2)
    
    def ai_action(self):
        playerColor = self.get_turn()
        if playerColor == 1:
            return self.blackAI(self.get_board())
        return self.whiteAI(self.get_board())
        
    def simulate_game(self, game_num):
        win_cnt = {0:0, 1:0, -1:0}
        for i in range(game_num):
            self.__init__(self.height, self.width)
            while not self.is_terminal():
                self.check_move() # 輪空規則
                if self.get_hint():
                    # 防呆: 裡層檢查是否有合法棋步才call ai
                    best_move = self.ai_action()
                    self.make_move(*best_move)
            winner = self.state.winner(1)
            print(f'第{i+1}場game{winner}贏')
            win_cnt[winner] += 1
        print(win_cnt)
                
if __name__ == '__main__':
    game = Reversi_Game(8,8)
    game.simulate_game(50)
    
    
    
    
    
    