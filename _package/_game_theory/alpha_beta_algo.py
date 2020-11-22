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
       - def next_turn(self): 切換至對手的回合 (用來解「輪空」規則)
    * game
       - def getValidMoves(self, state): 回傳一個字典，key值是行動，value是一個action_key，用來走棋或還原state
       - def evaluation_function(self, state, player_color): 回傳此盤面對「player_color」來說的分數，盤面愈好分數愈高
       - def is_terminal(self, state): 判斷一場遊戲是否已經結束
       - def makeMove(self, state, action_key): 自定義action_key行動
       - def unMakeMove(self, state, action_key): 此函數的用意是state可以還原，就只需創建一次，避免需要大量複製state而耗時
    """
    
    def __init__(self, max_depth, player_color, game, state):
        """
        Initiation
        Parameters
        ----------
        max_depth : int
            The max depth of the tree
        player_color : int(usually 1 or 2, 0 for empty grid)
            The player's index as MAX in minimax algorithm
        """
        self.max_depth = max_depth
        self.player_color = player_color
        self.game = game
        self.state = state
        self.node_expanded = 0
 
    def choose_action(self):
        """ 回傳(行動, state) """
        self.node_expanded = 0
 
        start_time = time.time()
 
        print("MINIMAX AB : Wait AI is choosing")
        list_action = self.game.getValidMoves(self.state)
        eval_score, selected_key_action = self._minimax(0,True,float('-inf'),float('inf'))
        print(f"MINIMAX : Done, eval = {eval_score}, expanded {self.node_expanded} nodes")
        eval_time = max(0.00001, time.time() - start_time)
        print(f"--- {eval_time} seconds ---, avg: {self.node_expanded/eval_time} (explode_node per seconds)")
        self.game.makeMove(self.state, list_action[selected_key_action])
        return (selected_key_action, self.state)
 
    def _minimax(self, current_depth, is_max_turn, alpha, beta):
        
        self.node_expanded += 1
 
        if current_depth == self.max_depth or self.game.is_terminal(self.state):
            return self.game.evaluation_function(self.state, self.player_color), ""
 
        possible_action = self.game.getValidMoves(self.state)
        key_of_actions = list(possible_action.keys())
        
        """ 若為pass或是單行道的情形，深度往後搜一層 """
        depth = current_depth if len(key_of_actions)<=1 else current_depth+1
        
        if not key_of_actions:
            """ 處理棋局還未結束，但無棋步可走而換對手的情形(ex: 黑白棋) """
            self.state.next_turn()
            eval_child, action_child = self._minimax(depth, not is_max_turn, alpha, beta)
            self.state.next_turn()
            
            best_value, action_target  = eval_child, ""
                
            if is_max_turn:
                alpha = max(alpha, best_value)
            else:
                beta = min(beta, best_value)
            return best_value, action_target
            
 
        random.shuffle(key_of_actions) #randomness
        best_value = float('-inf') if is_max_turn else float('inf')
        action_target = ""
        
        
        for action_key in key_of_actions:
            
            self.game.makeMove(self.state, possible_action[action_key])
            eval_child, action_child = self._minimax(depth, not is_max_turn, alpha, beta)
            self.game.unMakeMove(self.state, possible_action[action_key])
            
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