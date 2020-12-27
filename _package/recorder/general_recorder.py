import json

class Recorder():
    """
    用來記錄棋局過程，必要記錄的三項東西:
    「下一步換誰走0、」「初始盤面」、「棋局棋步」(可以做為state的getValidMoves()函數的key值去走棋的)
    目前假設一定是黑白交錯進行(如有輪空規則，記錄裡要寫'PASS')
    """
    
    def __init__(self, state, playerColor, board=None, debug=False):
        if board:
            self.reset(board)
        self.state = state
        self.playerColor = playerColor # 初始輪到誰走棋
        self.step_stack = []
        self.step_pt = 0 #當前在第幾步(實作悔棋、下一步功能)
        self.debug = debug
    
    def record_move(self, move):
        self.step_stack.append(move)
        self.step_pt += 1
        
    def reset(self, board):
        H, W = len(board), len(board[0])
        self.board = [[0]*W for i in range(H)]
        for r in range(H):
            for c in range(W):
                self.board[r][c] = board[r][c]
        self.step_stack = []
        self.step_pt = 0
    
    def __goto_move(self, n):
        # 從初始盤面開始擺n手棋
        self.state.__init__(self.board, self.playerColor)
        step_stack = self.step_stack
        for i in range(self.step_pt):
            valid_moves = self.state.getValidMoves()
            move = step_stack[i]
            if isinstance(move, list):
                move = tuple(move)
            if self.debug:
                print(f'[DEBUG] turn: {self.state.playerColor}, move: {move}')
            if move in valid_moves:
                self.state.makeMove(valid_moves[move])
            else:
                raise Exception('catch a non-valid move.')
    
    def back_move(self):
        self.step_pt = max(0, self.step_pt-1)
        self.__goto_move(self.step_pt)
        return self.state
    
    def next_move(self):
        self.step_pt = min(len(self.step_stack), self.step_pt+1)
        self.__goto_move(self.step_pt)
        return self.state
    
    def get_last_move(self):
        if self.step_stack:
            return self.step_stack[-1]
        
    def save(self, path):
        json.dump((self.playerColor, self.board, self.step_stack), open(path, "w"))
        
    
    def load(self, path):
        self.playerColor, self.board, self.step_stack = json.load(open(path, "r"))
        
        