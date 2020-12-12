class Recorder():
    
    def __init__(self, board):
        self.board = self.reset(board)
        self.step_stack = []
    
    def record_move(self, r,c):
        self.step_stack.append((r,c))
        print(f"[DEBUG] {self.step_stack}")
        
    def reset(self, board):
        H, W = len(board), len(board[0])
        self.board = [[0]*H for i in range(H)]
        for r in range(H):
            for c in range(W):
                self.board = board[r][c]
        self.step_stack = []
        
    def save(self):
        pass
    
    def load(self):
        pass
        