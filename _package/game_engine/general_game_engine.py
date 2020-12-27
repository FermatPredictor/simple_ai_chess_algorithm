# -*- coding: utf-8 -*-
import sys
sys.path.append('../..') # 添加相對路徑上兩層到sys.path，讓程式找到的模組_package

from _package.recorder.general_recorder import Recorder

class Game_Engine():
    
    """
    支援棋類對戰邏輯，存讀檔功能，
    可用於pygame接口。
    ai的部分需實作函數可吃參數(board, playerColor)，可以回傳棋步座標
    若無傳入ai的函數則使用默認的ab演算法
    
    只要定義好state(遊戲規則)，就可以接於pygame做視覺化。
    PASS棋步的key值以字串'PASS'表示
    
    state函數說明:
    - playerColor:  int(usually 1 or 2, 0 for empty grid), 下一步換誰下
    - getValidMoves(self): 下一步有哪些合法棋步可走，回傳字典:{合法棋步座標: 翻轉的對手棋子}，
                           通常是各ai算法的核心，很值得優化速度
    - makeMove(self, action_key): 根據action_key走棋 
    - unMakeMove(self, action_key): 根據同一個action_key還原棋步，通常用於alpha_beta算法避免創建過多state
    - passMove(self): 沒棋步可走，PASS
    - is_terminal(self): 判斷遊戲是否結束了
    - winner(self, tile): 遊戲結束的狀況下，判斷贏家是誰(0 for 和棋)
    - next_turn(self): 若遇到輪空的狀況，換下一個玩家行動
    - to_board(self): 取得可視覺化印出的board(比如說，為了計算快速，state內用一維list，但為了視覺化直覺用二維list)
    """
    def __init__(self, state, black_ai=None, white_ai=None):
        self.state = state
        self.recorder = Recorder(self.state)
        self.b_engine = black_ai if black_ai else None
        self.w_engine = white_ai if white_ai else None
        
    def make_move(self, r,c, raise_except=False):
        valid_moves = self.state.getValidMoves()
        if (r,c) in valid_moves:
            self.state.makeMove(valid_moves[(r,c)])
            self.recorder.refresh()
            self.recorder.record_move((r,c))
        elif raise_except:
            raise Exception('The move is not valid.')
            
    def change_turn(self):
        """
        觸發條件: 一方無棋可走，自動換下一方走。
        或者手動按PASS鈕觸發
        """
        self.state.passMove()
        self.recorder.record_move('PASS')

    def check_move(self):
        """
        輪空規則，觸發時機在主遊戲迴圈被call。
        """   
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
    
    def save(self, path):
        self.recorder.save(path)
        print(f'save the file {path}')
        
    def load(self, path):
        self.recorder.load(path)
        print(f'load the file {path}')
        
    def back_move(self):
        self.state = self.recorder.back_move()
    
    def next_move(self):
        self.state = self.recorder.next_move()
        
    def reset_record(self):
        self.recorder.reset(self.state)
        
    def get_last_move(self):
        # 用於ui中棋盤標記上一步棋
        return self.recorder.get_last_move()
    
    def ai_action(self, make_move = True):
        playerColor = self.get_turn()
        if not self.b_engine and playerColor == 1:
            raise Exception('The game not support black engine')
        if not self.w_engine and playerColor == 2:
            raise Exception('The game not support white engine')
        ai_engine = self.b_engine if playerColor == 1 else self.w_engine
        best_move = ai_engine(self.get_board(), playerColor)
        if not make_move:
            return best_move
        self.make_move(*best_move)
        
    def game_loop(self,  black_ai: bool, white_ai:bool)->bool:
        """
        觸發時機: 於pygame的主迴圈不斷執行
        當遊戲已結束時回傳False
        """
        def is_ai_turn():
            return self.get_turn()==1 and black_ai or self.get_turn()==2 and white_ai
            
        if not self.is_terminal():
            if self.recorder.is_last_move():
                """
                基於本game engine與recorder綁定，
                所以應該在沒有按「上一步」的情況下才自動跳步，
                否則棋局會一直自動新增「PASS」而無法回「上一步」。
                同時，按「上一步」的狀況下暫停ai走棋。
                """
                self.check_move() # 輪空規則
                if self.get_hint():
                    # 防呆: 合法棋步時才call ai
                    if is_ai_turn():
                        self.ai_action()
            return True
        return False
