import sys
import os
sys.path.append('..') # 添加相對路徑上兩層到sys.path，讓程式找到的模組_package

from pprint import pprint
from datetime import datetime

from Basic_Game_Logic.reversi_fast_ab import ab_action
from Basic_Game_Logic.reversi_mcts import mcts_action
from Basic_Game_Logic.reversi_fast_ab import AB_ReversiState
from _package.game_engine.general_game_engine import Game_Engine

def time_now():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def reversi_init_game(height, width, black_ai=None, white_ai=None):
    board = [[0]*width for _ in range(height)]
    H, W = height//2, width//2
    board[H-1][W-1], board[H-1][W] = 2, 1
    board[H][W-1], board[H][W] = 1, 2
    state = AB_ReversiState(board, 1)
    return Game_Engine(state, black_ai, white_ai)

        
def simulate_game(game_num):
    win_cnt = {0:0, 1:0, -1:0}
    for i in range(game_num):
        game = reversi_init_game(6,6, ab_action, mcts_action)
        while not game.is_terminal():
            game.check_move() # 輪空規則
            if game.get_hint():
                # 防呆: 裡層檢查是否有合法棋步才call ai
                game.ai_action()
        winner = game.state.winner(1)
        print(f'第{i+1}場game{winner}贏')
        win_cnt[winner] += 1
        print(win_cnt)
        game.save(os.path.join('.\\',time_now()+'.json'))
        
def load_game_test():
    game = reversi_init_game(6,6)
    game.load(r'.\2020-12-27_13-12-19.json')
    for i in range(36):
        game.next_move()
        print(i)
        pprint(game.get_board())
                
if __name__ == '__main__':
    simulate_game(2)
    #load_game_test()

    
    
    
    
    
    