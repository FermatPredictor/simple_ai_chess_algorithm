import time
import random

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
        
    def isOnBoard(self, r, c):
        return 0 <= r < self.height and 0 <= c < self.width
    
    #檢查tile放在某個座標是否為合法棋步，如果是則回傳翻轉的對手棋子
    def isValidMove(self, r, c):
        if not self.isOnBoard(r,c) or self.board[r][c]!=0:
            return False
        tile, opp_tile = self.playerColor , self.opp_color()
        tilesToFlip = []
        dirs = [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]] # 定義八個方向
        for dr, dc in dirs:
            _r, _c, flip = r+dr, c+dc, 0
            while self.isOnBoard(_r, _c) and self.board[_r][_c] == opp_tile:
                tilesToFlip.append([_r, _c])
                _r, _c, flip = _r+dr, _c+dc, flip+1
            if flip>0 and not(self.isOnBoard(_r, _c) and self.board[_r][_c] == tile):
               tilesToFlip = tilesToFlip[:-flip] # 沒夾到對手的棋子，抹去記錄
        if tilesToFlip:
            return [[r, c]] + tilesToFlip
        return False
    
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
        moves = {(x, y):self.isValidMove(x,y) for x in range(self.height) for y in range(self.width)}
        move_fliter = {k:(v, self.pass_info) for k,v in moves.items() if v}
        return move_fliter if move_fliter else {'PASS': ('PASS', self.pass_info)}
    
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
        score, opp, w_board = 0, tile^3, self.__get_weight_board()
        for r in range(self.height):
            for c in range(self.width):
                coef = {0:0, tile: 1, opp:-1} 
                score += w_board[r][c]* coef[self.board[r][c]] if self.eval_mode == 'weight' else 1
        return score
        
    
    def is_terminal(self):
        return self.pass_info == 3

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
        player_color : int(usually 1 or 2, 0 for empty grid)
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
        self.state.makeMove(list_action[selected_key_action])
        return selected_key_action
 
    def _minimax(self, current_depth, is_max_turn, alpha, beta):
        
        self.node_expanded += 1
 
        if current_depth == self.max_depth or self.state.is_terminal():
            return self.state.evaluation_function(self.player_color), ""
 
        possible_action = self.state.getValidMoves()
        key_of_actions = list(possible_action.keys())
        
        """ 若為pass或是單行道的情形，深度往後搜一層 """
        depth = current_depth if len(key_of_actions)<=1 else current_depth+1            
 
        random.shuffle(key_of_actions) #randomness
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
    
if __name__=='__main__':
    play_color = 1
    board = [[0,0,0,0,0,0,0,0],
              [0,0,0,0,0,0,0,0],
              [0,0,0,1,0,0,0,0],
              [0,0,2,2,2,2,0,0],
              [0,0,0,1,2,0,0,0],
              [0,0,0,0,0,0,0,0],
              [0,0,0,0,0,0,0,0],
              [0,0,0,0,0,0,0,0]]
    state = ReversiState(board, play_color)
    AI = MinimaxABAgent(3, play_color, state)
    result = AI.choose_action()
