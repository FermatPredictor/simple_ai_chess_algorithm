import sys
sys.path.append('..') # 添加相對路徑上兩層到sys.path，讓程式找到的模組_package

from Basic_Game_Logic.reversi_fast_ab import ab_action
from Basic_Game_Logic.reversi_mcts import mcts_action

from reversi_game import Reversi_Game

        
def simulate_game(game_num):
    win_cnt = {0:0, 1:0, -1:0}
    for i in range(game_num):
        game = Reversi_Game(6,6, ab_action, mcts_action)
        while not game.is_terminal():
            game.check_move() # 輪空規則
            if game.get_hint():
                # 防呆: 裡層檢查是否有合法棋步才call ai
                best_move = game.ai_action()
                game.make_move(*best_move)
        winner = game.state.winner(1)
        print(f'第{i+1}場game{winner}贏')
        win_cnt[winner] += 1
        print(win_cnt)
        game.save()
                
if __name__ == '__main__':
    simulate_game(2)

    
    
    
    
    
    