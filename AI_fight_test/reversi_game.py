import os
from datetime import datetime
from pprint import pprint

import sys
sys.path.append('..') # 添加相對路徑上兩層到sys.path，讓程式找到的模組_package

from Basic_Game_Logic.reversi_fast_ab import AB_ReversiState
from Basic_Game_Logic.reversi_fast_ab import ab_action
from Basic_Game_Logic.reversi_mcts import mcts_action

from general_recorder import Recorder


def time_now():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


class Reversi_Game():
    
    """
    支援黑白棋對戰邏輯，存讀檔功能，
    可用於pygame接口。
    ai的部分需實作函數可吃參數(board, playerColor)，可以回傳棋步座標
    若無傳入ai的函數則使用默認的ab演算法
    """
    def __init__(self, height, width, black_ai=None, white_ai=None):
        self.height, self.width = height, width
        board = [[0]*width for _ in range(height)]
        H, W = height//2, width//2
        board[H-1][W-1], board[H-1][W] = 2, 1
        board[H][W-1], board[H][W] = 1, 2
        self.board = board
        self.state = AB_ReversiState(board, 1)
        self.recorder = Recorder(self.state, board)
        self.b_engine = black_ai if black_ai else ab_action
        self.w_engine = white_ai if white_ai else ab_action
        
    def make_move(self, r,c):
        valid_moves = self.state.getValidMoves()
        if (r,c) in valid_moves:
            self.state.makeMove(valid_moves[(r,c)])
            self.recorder.record_move((r,c))
        else:
            raise Exception('The move is not valid.')
            
    def change_turn(self):
        self.state.makeMove(('PASS', 0))

    def check_move(self):
        # 輪空規則
        valid_moves = self.get_hint()
        if not valid_moves:
            self.change_turn()
            self.recorder.record_move('PASS')
    
    def get_hint(self):
        return set(self.state.getValidMoves()) - {'PASS'}
    
    def get_turn(self):
        return self.state.playerColor
    
    def get_board(self):
        return self.state.to_board()
    
    def is_terminal(self):
        return self.state.is_terminal()
    
    def save(self):
        self.recorder.save(os.path.join('.\\',time_now()+'.json'))
        
    def load(self, path):
        self.recorder.load(path)
        
    def back_move(self):
        self.state = self.recorder.back_move()
    
    def next_move(self):
        self.state = self.recorder.next_move()
        
    def get_last_move(self):
        # 用於ui中棋盤標記上一步棋
        return self.recorder.get_last_move()
    
    def ai_action(self):
        playerColor = self.get_turn()
        ai_engine = self.b_engine if playerColor == 1 else self.w_engine
        return ai_engine(self.get_board(), playerColor)

if __name__ == '__main__':
    game = Reversi_Game(6,6)
    game.load(r'.\2020-12-20_22-32-37.json')
    for i in range(36):
        game.next_move()
        print(i)
        pprint(game.get_board())