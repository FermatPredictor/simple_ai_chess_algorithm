import json
import os
from datetime import datetime
from pprint import pprint

import sys
sys.path.append('..') # 添加相對路徑上兩層到sys.path，讓程式找到的模組_package

from Basic_Game_Logic.reversi_fast_ab import AB_ReversiState
from Basic_Game_Logic.reversi_fast_ab import ab_action
from Basic_Game_Logic.reversi_mcts import mcts_action


def time_now():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

"""
本程式讓不同ai進行對局測試，
是「裁判」的角色，
支援黑白棋對戰邏輯，存讀檔功能，
可用於pygame接口
"""

class Recorder():
    
    def __init__(self, board=None):
        if board:
            self.reset(board)
        self.step_stack = []
    
    def record_move(self, r,c):
        self.step_stack.append((r,c))
        print(f"[DEBUG] {self.step_stack}")
        
    def reset(self, board):
        H, W = len(board), len(board[0])
        self.board = [[0]*W for i in range(H)]
        for r in range(H):
            for c in range(W):
                self.board[r][c] = board[r][c]
        self.step_stack = []
        
    def get_step_num(self):
        return len(self.step_stack)
    
    def get_step_stack(self):
        return self.step_stack
        
    def save(self, path):
        json.dump((self.board, self.step_stack), open(path, "w"))
        
    
    def load(self, path):
        self.board, self.step_stack = json.load(open(path, "r"))
        self.step_stack = list(map(tuple, self.step_stack))

class Reversi_Game():
    def __init__(self, height, width):
        self.height, self.width = height, width
        board = [[0]*width for _ in range(height)]
        H, W = height//2, width//2
        board[H-1][W-1], board[H-1][W] = 2, 1
        board[H][W-1], board[H][W] = 1, 2
        self.board = board
        self.state = AB_ReversiState(board, 1)
        self.recorder = Recorder(board)
        self.step_pt = 0 #當前在第幾步(實作悔棋、下一步功能)
        
    def make_move(self, r,c):
        valid_moves = self.state.getValidMoves()
        if (r,c) in valid_moves:
            self.state.makeMove(valid_moves[(r,c)])
            self.recorder.record_move(r,c)
            self.step_pt += 1
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
    
    def save(self):
        self.recorder.save(os.path.join('.\\',time_now()+'.json'))
        
    def load(self, path):
        self.recorder.load(path)
        self.step_pt = 0
        
    def back_move(self):
        self.step_pt = max(0, self.step_pt-1)
        self.state = AB_ReversiState(self.board, 1)
        step_stack = self.recorder.get_step_stack()
        for i in range(self.step_pt):
            valid_moves = self.state.getValidMoves()
            if step_stack[i] in valid_moves:
                self.state.makeMove(valid_moves[step_stack[i]])
            else:
                raise Exception('catch a non-valid move.')
    
    def next_move(self):
        self.step_pt = min(self.recorder.get_step_num(), self.step_pt+1)
        self.state = AB_ReversiState(self.board, 1)
        step_stack = self.recorder.get_step_stack()
        for i in range(self.step_pt):
            valid_moves = self.state.getValidMoves()
            if step_stack[i] in valid_moves:
                self.state.makeMove(valid_moves[step_stack[i]])
            else:
                raise Exception('catch a non-valid move.')
        
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
            self.save()
                
if __name__ == '__main__':
    game = Reversi_Game(6,6)
    #game.simulate_game(5)
    game.load(r'.\2020-12-20_11-32-45.json')
    for i in range(5):
        game.next_move()
        pprint(game.get_board())
    
    
    
    
    
    
    