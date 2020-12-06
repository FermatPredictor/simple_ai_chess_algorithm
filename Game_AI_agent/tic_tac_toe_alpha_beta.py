import sys
sys.path.append('..') # 添加相對路徑上兩層到sys.path，讓程式找到的模組_package
from _package._game_theory.alpha_beta_algo import MinimaxABAgent

class State():
    """ 
    記錄棋盤資訊，及下一步換誰下
    player_color : int(usually 1 or 2, 0 for empty grid)
    """
    def __init__(self, board, playerColor):
        self.board = board
        self.playerColor = playerColor
    
    def opp_color(self):
        return 3^self.playerColor
    
    def next_turn(self):
        self.playerColor = self.opp_color()


class TicTacToe():
    def __init__(self):
        pass
    
    def isOnBoard(self, x, y):
        return 0 <= x < 3 and 0 <= y < 3
        
    #檢查tile放在某個座標是否為合法棋步
    def isValidMove(self, state, x, y):
        return self.isOnBoard(x, y) and state.board[x][y]==0
    
    def makeMove(self, state, action_key):
        x,y = action_key
        state.board[x][y] = state.playerColor
        state.playerColor = state.opp_color()
    
    def unMakeMove(self, state, action_key):
        x,y = action_key
        state.board[x][y] = 0
        state.playerColor = state.opp_color()
    
    # 回傳現在盤面輪到tile走的所有合法棋步
    def getValidMoves(self, state):
        return {(x, y):(x, y) for x in range(3) for y in range(3) if self.isValidMove(state, x, y)}

    # 判斷一個盤面是否有人贏了
    def check_TicTacToe(self, state):
        rows = list(map(lambda x: ''.join(map(str,x)), state.board))
        cols = list(map(''.join, zip(*rows)))
        diags = list(map(''.join, zip(*[(r[i], r[2 - i]) for i, r in enumerate(rows)])))
        lines = rows + cols + diags
    
        if '111' in lines:
            return 1 
        if '222' in lines:
            return 2
        return 'D' # draw(和棋)
    
    def evaluation_function(self, state, tile):
        if not self.is_terminal(state):
            return 0
        winner = self.check_TicTacToe(state)
        if winner == tile:
            return 100
        if winner == 'D':
            return 0
        return -100
    
    def is_terminal(self, state):
        if self.check_TicTacToe(state) in [1,2]:
            return True
        for i in range(3):
            for j in range(3):
                if state.board[i][j]==0:
                    return False
        return True
    
    
if __name__=='__main__':
    """
    井字棋套用alpha-beta算法
    通過 https://www.hackerrank.com/challenges/tic-tac-toe/problem 的測試
    """
    play_color = 1
    board = [[0,0,2],
             [0,0,0],
             [0,0,0]]
    state = State(board, play_color)
    game = TicTacToe()
    AI = MinimaxABAgent(8, play_color, game, state)
    result = AI.choose_action()
    
