import numpy as np
from collections import defaultdict
from copy import deepcopy
from pprint import pprint
import time

import cProfile

class ReversiState():
    """ 
    player_color : int(usually 1 or 2, 0 for empty grid), 下一步換誰下
    """
    def __init__(self, board, playerColor):
        self.board = board
        self.height, self.width = len(board), len(board[0])
        self.playerColor = playerColor
        self.eval_mode = 'weight'
        self.pass_info = 0 # 0:無pass, 1:黑pass, 2:白pass, 3:黑白均pass，此時game over 
        self.w_board = self.__get_weight_board()
        
    def isOnBoard(self, r, c, H, W):
        return 0 <= r < H and 0 <= c < W
    
    def makeMove(self, action_key):
        key, pass_info = action_key
        if key != 'PASS':
            for r, c in key:
                self.board[r][c] = self.playerColor
            self.pass_info = 0
        else:
            self.pass_info = self.pass_info | self.playerColor
        self.next_turn()
            
    def unMakeMove(self, action_key):
        key, pass_info = action_key
        self.pass_info = pass_info
        if key != 'PASS':
            _r, _c = key[0]
            self.board[_r][_c] = 0
            for r, c in key[1:]:
                self.board[r][c] = self.playerColor
        self.next_turn()
    
    def getValidMoves(self):
        """
        回傳字典: {合法棋步座標: 翻轉的對手棋子}
        算法改進: 
         As is: 檢查棋盤上的所有格子
         To be: 先定位自己棋子，往八個方向搜索是否夾到對手棋子
        效能: 與上一版相比大約快 3 倍
        """
        H, W = self.height, self.width
        tile, opp_tile = self.playerColor , self.opp_color()
        move_dict = {}
        dirs = [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]] # 定義八個方向
        for r in range(H):
            for c in range(W):
                if self.board[r][c]!=tile:
                    continue
                for dr, dc in dirs:
                    _r, _c, flip = r+dr, c+dc, 0
                    while self.isOnBoard(_r, _c, H, W) and self.board[_r][_c] == opp_tile:
                        _r, _c, flip = _r+dr, _c+dc, flip+1
                    if flip and self.isOnBoard(_r, _c, H, W) and self.board[_r][_c] == 0:
                        # 夾到對手的棋子，回頭記錄
                        if (_r, _c) not in move_dict:
                            move_dict[(_r, _c)] = [(_r, _c)] 
                        grid_r, gird_c = _r, _c
                        for i in range(flip):
                            _r, _c = _r-dr, _c-dc
                            move_dict[(grid_r, gird_c)].append((_r, _c))
        move_dict = {k:(v, self.pass_info) for k,v in move_dict.items()}
        return move_dict if move_dict else {'PASS': ('PASS', self.pass_info)}
                

                
    def opp_color(self):
        return 3^self.playerColor
    
    def next_turn(self):
        self.playerColor = self.opp_color()
    
    def __spiral_coords(self, board, r1, c1, r2, c2, weights):
        """
        遍歷矩陣之外圈，
        並將角、C位、邊設權重
        """
        def Pos(r,c):
            if r in [r1+1, r2-1] or c in [c1+1,c2-1]:
                return 1
            return 2
                
        for c in range(c1, c2 + 1):
            board[r1][c] = weights[Pos(r1,c)]
        for r in range(r1 + 1, r2 + 1):
            board[r][c2] = weights[Pos(r,c2)]
        for c in range(c2 - 1, c1, -1):
            board[r2][c] = weights[Pos(r2,c)]
        for r in range(r2, r1, -1):
            board[r][c1] = weights[Pos(r,c1)]
        board[r1][c1], board[r1][c2], board[r2][c1], board[r2][c2] = [weights[0]]*4
    
    def __get_weight_board(self):
        """
        這邊手動調整格子對應的權重分配，
        對應「角、C位、邊、星位、中央邊、中央」
        """
        if self.width<6 and self.height<6:
            # 棋盤過小，直接數棋子數
            return [[1]*self.width for _ in range(self.height)]
            
        weights = [100,-10,20,-50,-2, 1]
        w_board = [[weights[5]]*self.width for _ in range(self.height)]
        self.__spiral_coords(w_board, 0,0,self.height-1, self.width-1, weights[:3])
        self.__spiral_coords(w_board, 1,1,self.height-2, self.width-2, weights[3:5]+[weights[4]])
        return w_board
        
    def evaluation_function(self, tile):
        score, opp = 0, tile^3
        coef = {0:0, tile: 1, opp:-1} 
        for r in range(self.height):
            for c in range(self.width):
                score += (self.w_board[r][c] if self.eval_mode == 'weight' else 1)* coef[self.board[r][c]]
        return score
    
    def winner(self, tile):
        score, opp = 0, tile^3
        coef = {0:0, tile: 1, opp:-1} 
        for r in range(self.height):
            for c in range(self.width):
                score += 1* coef[self.board[r][c]]
        if score>0:
            return -1
        if score<0:
            return 1
        return 0  
        
    def is_terminal(self):
        return self.pass_info == 3


class MonteCarloTreeSearchNode(object):
    """
    MonteCarloTreeSearch 演算法模版，
    用途是只要定義好遊戲規則，
    ai就會透過此演算法計算最佳行動(棋步)
    
    必要定義的物件:
    * state: 類似指標可以inplace修改的物件
       - def getValidMoves(self): 回傳一個字典，key值是行動，value是一個action_key，用來走棋或還原state
       - def is_terminal(self): 判斷一場遊戲是否已經結束
       - def makeMove(self, action_key): 自定義action_key行動
       - def unMakeMove(self, action_key): 此函數的用意是state可以還原，就只需創建一次，避免需要大量複製state而耗時
    """
    def __init__(self, state, parent=None, action=None):
        self._number_of_visits = 0.
        self._results = defaultdict(int) #1:win, -1:lose, 0: draw
        self.state = state
        self.parent = parent
        self.action = action
        self.children = []

    @property
    def untried_actions(self):
        if not hasattr(self, '_untried_actions'):
            self._untried_actions = list(self.state.getValidMoves().values())
        return self._untried_actions

    @property
    def q(self):
        wins, loses = self._results[1], self._results[-1]
        return wins # ins-loses

    @property
    def n(self):
        return self._number_of_visits

    def expand(self):
        action = self.untried_actions.pop()
        cur_state = deepcopy(self.state)
        cur_state.makeMove(action)
        child_node = MonteCarloTreeSearchNode(cur_state, parent=self, action=action)
        self.children.append(child_node)
        return child_node

    def is_terminal_node(self):
        return self.state.is_terminal()

    def rollout(self):
        player_color = self.state.playerColor
        cur_state = deepcopy(self.state)
        print('rollout前')
        print(player_color)
        pprint(cur_state.board)
        while not cur_state.is_terminal():
            possible_moves = list(cur_state.getValidMoves().values())
            action = self.rollout_policy(possible_moves)
            cur_state.makeMove(action)
        print('rollout後')
        print(player_color)
        pprint(cur_state.board)
        return cur_state.winner(player_color)

    def backpropagate(self, result):
        self._number_of_visits += 1.
        self._results[result] += 1.
        if self.parent:
            self.parent.backpropagate(-result)

    def is_fully_expanded(self):
        return not self.untried_actions

    def best_child(self, c_param=1.4):
        choices_weights = [
            (c.q / (c.n)) + c_param * np.sqrt((2 * np.log(self.n) / (c.n)))
            for c in self.children
        ]
        return self.children[np.argmax(choices_weights)]

    def rollout_policy(self, possible_moves):
        return possible_moves[np.random.randint(len(possible_moves))]
    
class MonteCarloTreeSearch:
    def __init__(self, node: MonteCarloTreeSearchNode):
        self.root = node

    def best_action(self, simulations_number):
        start_time = time.time()
        for _ in range(simulations_number):
            v = self.tree_policy()
            reward = v.rollout()
            v.backpropagate(reward)
        eval_time = max(0.00001, time.time() - start_time)
        print(f"--- {eval_time} seconds ---, avg: {simulations_number/eval_time} (explode_node per seconds)")
        # exploitation only
        for c in self.root.children:
            print(c.action, c.q, c.n, c.q/c.n)
        return self.root.best_child(c_param=0.)

    def tree_policy(self):
        current_node = self.root
        while not current_node.is_terminal_node():
            if not current_node.is_fully_expanded():
                return current_node.expand()
            else:
                current_node = current_node.best_child()
        return current_node

def main():
    play_color = 1
    # board = [[0,2,1,2,0,0,0,0],
    #           [0,0,0,0,0,0,0,0],
    #           [0,0,0,0,0,0,0,0],
    #           [0,0,0,0,0,0,0,0],
    #           [0,0,0,0,0,0,0,0],
    #           [0,0,0,0,0,0,0,0],
    #           [0,0,0,0,0,0,0,0],
    #           [0,0,0,0,0,0,0,0]]
    board = [[0,0,0,0,0,0,0,0],
              [0,0,0,0,0,0,0,0],
              [0,0,0,1,0,0,0,0],
              [0,0,2,2,2,2,0,0],
              [0,0,0,1,2,0,0,0],
              [0,0,0,0,0,0,0,0],
              [0,0,0,0,0,0,0,0],
              [0,0,0,0,0,0,0,0]]
    """
    board = [[2,2,2,2,2,2,2,2],
             [1,1,1,1,2,1,2,2],
             [1,1,2,2,2,2,1,2],
             [0,1,1,2,2,1,2,2],
             [0,1,1,2,1,2,2,2],
             [1,1,2,2,2,2,2,2],
             [1,1,1,1,1,2,0,2],
             [2,2,2,2,2,2,0,0]]
    """
    state = ReversiState(board, play_color)
    AI = MonteCarloTreeSearch(MonteCarloTreeSearchNode(state))
    result = AI.best_action(500)
    pprint(result.action)
    

if __name__=='__main__':
    main()
    #cProfile.run('main()')