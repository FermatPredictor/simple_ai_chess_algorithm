import time
import random

""" ref: https://www.mygreatlearning.com/blog/alpha-beta-pruning-in-ai/ """
class MinimaxABAgent:
    """
    alpha beta 演算法模版，
    用途是只要定義好遊戲規則，
    ai就會透過此演算法計算最佳行動(棋步)
    
    必要定義的物件:
    * state: 類似指標可以inplace修改的物件
       - def getValidMoves(self): 回傳一個字典，key值是行動，value是一個action_key，用來走棋或還原state
       - def evaluation_function(self, player_color): 回傳此盤面對「player_color」來說的分數，盤面愈好分數愈高
       - def is_terminal(self): 判斷一場遊戲是否已經結束
       - def makeMove(self, action_key): 自定義action_key行動
       - def unMakeMove(self, action_key): 此函數的用意是state可以還原，就只需創建一次，避免需要大量複製state而耗時
    """
    
    def __init__(self, max_depth, player_color, state):
        """
        Initiation
        Parameters
        ----------
        max_depth : int
            The max depth of the tree
        player_color : int(usually 1 or 2)
            The player's index as MAX in minimax algorithm
        """
        self.max_depth = max_depth
        self.player_color = player_color
        self.state = state
        self.node_expanded = 0
 
    def choose_action(self):
        """ 回傳 action """
        self.node_expanded = 0
 
        start_time = time.time()
 
        print("MINIMAX AB : Wait AI is choosing")
        list_action = self.state.getValidMoves()
        eval_score, selected_key_action = self._minimax(0,True,float('-inf'),float('inf'))
        print(f"MINIMAX : Done, eval = {eval_score}, expanded {self.node_expanded} nodes")
        eval_time = max(0.00001, time.time() - start_time)
        print(f"--- {eval_time} seconds ---, avg: {self.node_expanded/eval_time} (explode_node per seconds)")
        print(f'The best move is {selected_key_action}')
        self.state.makeMove(list_action[selected_key_action])
        return selected_key_action
 
    def _minimax(self, current_depth, is_max_turn, alpha, beta):
        
        self.node_expanded += 1
 
        if current_depth == self.max_depth or self.state.is_terminal():
            return self.state.evaluation_function(self.player_color), "PASS"
 
        possible_action = self.state.getValidMoves()
        key_of_actions = list(possible_action.keys())
        
        """ 若為pass或是單行道的情形，深度往後搜一層 """
        depth = current_depth if len(key_of_actions)<=1 else current_depth+1            
 
        #random.shuffle(key_of_actions) #randomness
        best_value = float('-inf') if is_max_turn else float('inf')
        action_target = ""
        
        for action_key in key_of_actions:
            
            self.state.makeMove(possible_action[action_key])
            eval_child, action_child = self._minimax(depth, not is_max_turn, alpha, beta)
            self.state.unMakeMove(possible_action[action_key])
            
            max_condition = is_max_turn and best_value < eval_child
            min_condition = (not is_max_turn) and best_value > eval_child
            
            if max_condition or min_condition:
                best_value, action_target  = eval_child, action_key 
                
                if max_condition:
                    alpha = max(alpha, best_value)
                else:
                    beta = min(beta, best_value)
                    
                if beta <= alpha:       
                    break

        return best_value, action_target