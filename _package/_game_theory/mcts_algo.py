import numpy as np
from collections import defaultdict
from copy import deepcopy
import time
import random

class MonteCarloTreeSearchNode(object):
    """
    MonteCarloTreeSearch 演算法模版，
    用途是只要定義好遊戲規則，
    ai就會透過此演算法計算最佳行動(棋步)
    
    必要定義的物件:
    * state: 類似指標可以inplace修改的物件
       - def getValidMoves(self): 回傳一個字典，key值是行動，value是一個action_key，用來走棋或還原state
       - def is_terminal(self): 判斷一場遊戲是否已經結束
       - def winner(self, tile): 判斷tile的勝負，1是win，-1是lose，0是和局
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
            self._untried_actions = [(k, v) for k, v in self.state.getValidMoves().items()]
        return self._untried_actions

    @property
    def q(self):
        wins, loses = self._results[1], self._results[-1]
        return wins #wins-loses

    @property
    def n(self):
        return self._number_of_visits

    def expand(self):
        key, action = self.untried_actions.pop()
        cur_state = deepcopy(self.state)
        cur_state.makeMove(action)
        child_node = MonteCarloTreeSearchNode(cur_state, parent=self, action=(key, action))
        self.children.append(child_node)
        return child_node

    def is_terminal_node(self):
        return self.state.is_terminal()

    def rollout(self):
        player_color = self.state.playerColor
        cur_state = deepcopy(self.state)
        #print('rollout前')
        #print(player_color)
        #pprint(cur_state.board)
        while not cur_state.is_terminal():
            possible_moves = list(cur_state.getValidMoves().values())
            action = self.rollout_policy(possible_moves)
            cur_state.makeMove(action)
        #print('rollout後')
        #print(player_color)
        #pprint(cur_state.board)
        return -cur_state.winner(player_color)

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
        return random.choice(possible_moves)
    
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

